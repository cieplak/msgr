from collections import namedtuple
import functools
import json
import logging

import kombu
import kombu.mixins
import pika
import pika.credentials

from msgr import settings


logger = logging.getLogger(__name__)


def send(key, payload, exchange=settings.AMQP['EXCHANGE']):
    encoded_payload = json.dumps(payload).encode('utf8')
    with kombu.Connection(settings.AMQP['URI']) as cxn:
        producer = kombu.Producer(
            cxn,
            exchange=kombu.Exchange(exchange),
            routing_key=key,
            auto_declare=False,
            )
        producer.publish(
            encoded_payload,
            content_type='application/json',
            content_encoding='utf8',
            retry=True
        )


def receive(queue):
    def outer(inner):
        Engine.Consumer.register(queue, inner)
        return inner
    return outer


def process(limit=None):
    consumer = Engine.Consumer()
    if limit:
        return list(consumer.consume(limit=limit))
    return consumer.run()


class Engine(object):

    Queue = namedtuple('Queue', [
        'name',
        'exchange',
        'routing_key',
        'should_retry',
        ])

    cxn_params = pika.ConnectionParameters(
        host=settings.AMQP['IP_ADDRESS'],
        port=settings.AMQP['PORT'],
        credentials=pika.credentials.PlainCredentials(
            settings.AMQP['USER'],
            settings.AMQP['PASSWORD'],
            ),
        )

    deferred_suffix = '_deferred'

    dlx_suffix = '_dlx'

    @classmethod
    def create_exchanges(cls):
        cxn = pika.BlockingConnection(cls.cxn_params)
        channel = cxn.channel()
        channel.exchange_declare(exchange=settings.AMQP['EXCHANGE'], type='topic', durable=True)
        channel.exchange_declare(exchange=settings.AMQP['DEFERRED_EXCHANGE'], type='direct', durable=True)
        channel.exchange_declare(exchange=settings.AMQP['DLX_EXCHANGE'], type='direct', durable=True)
        cxn.close()

    queues = [Queue(*q) for q in settings.AMQP['QUEUES']]

    @classmethod
    def create_queue(cls, queue, retry_delay=10 * 60):  # ten minutes
        cxn = pika.BlockingConnection(cls.cxn_params)
        channel = cxn.channel()
        queue_name, exchange, routing_key, retry = tuple(queue)
        channel.queue_declare(
            queue=queue_name,
            durable=True,
            )
        if retry:
            channel.queue_declare(
                queue=queue_name + cls.deferred_suffix,
                durable=True,
                **{
                    'arguments': {
                        'x-dead-letter-exchange': settings.AMQP['DLX_EXCHANGE'],
                        'x-message-ttl': int(retry_delay) * 1000  # sec -> ms,
                    }
                }
            )
        channel.queue_bind(
            exchange=exchange,
            queue=queue_name,
            routing_key=routing_key,
            )
        if retry:
            channel.queue_bind(
                exchange=exchange + cls.deferred_suffix,
                queue=queue_name + cls.deferred_suffix,
                routing_key=queue_name,
                )
            channel.queue_bind(
                exchange=exchange + cls.dlx_suffix,
                queue=queue_name,
                routing_key=queue_name,
                )

    @classmethod
    def delete_queue(cls, queue_name):
        cxn = pika.BlockingConnection(cls.cxn_params)
        channel = cxn.channel()
        channel.queue_delete(queue=queue_name)

    class Consumer(kombu.mixins.ConsumerMixin):

        deferred_exchange = settings.AMQP['DEFERRED_EXCHANGE']

        registry = []

        @classmethod
        def register(self, queue, callback):
            subscriber = {
                'queue': queue,
                'callback': callback,
                }
            self.registry.append(subscriber)

        def __init__(self, qos=None):
            self.qos = qos or {'prefetch_count': 20}
            self.connection = kombu.Connection(settings.AMQP['URI'])

        def on_message(self, subscriber, body, message):
            try:
                return self._callback(subscriber, body)
            except Exception:
                self._retry(subscriber, body)
            finally:
                message.ack()

        def _callback(self, subscriber, body):
            subscriber['callback'](body)

        def _retry(self, subscriber, body):
            send(
                subscriber['queue'], body,
                exchange=self.deferred_exchange
            )

        def get_consumers(self, Consumer, channel):
            consumers = []
            for subscriber in self.registry:
                queue = kombu.Queue(subscriber['queue'])
                on_message = functools.partial(
                    self.on_message,
                    subscriber,
                    )
                consumer = Consumer(
                    queues=[queue],
                    callbacks=[on_message],
                    auto_declare=False,
                    )
                consumer.qos(**self.qos)
                consumers.append(consumer)
            return consumers