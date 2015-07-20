from __future__ import absolute_import
from collections import namedtuple
import json
import logging

import kafka as _kafka

from msgr import settings


logger = logging.getLogger(__name__)


def send(topic, message):
    producer = Engine.create_producer()
    encoded_message = json.dumps(message).encode('utf-8')
    return producer.send_messages(topic, encoded_message)


def receive(topic):
    def outer(inner):
        subscriber = Engine.Subscriber(func=inner, topic=topic)
        Engine.register(subscriber)
        return inner
    return outer


def process(limit=None, consumer=None):
    subscriber_by_topic = {s.topic: s.func for s in Engine.subscribers}
    consumer = consumer or Engine.create_consumer(*subscriber_by_topic)
    for idx, message in enumerate(consumer):
        callback = subscriber_by_topic.get(message.topic)
        if not callback:
            logger.warning('No receiver found for topic %s' % message.topic)
            continue
        callback(json.loads(message.value.decode('utf-8')))
        if limit and limit <= idx + 1:
            return


class Engine(object):

    subscribers = set()

    Subscriber = namedtuple('Subscriber', [
        'topic',
        'func',
        ])

    @classmethod
    def register(cls, subscriber):
        Engine.subscribers.add(subscriber)

    @classmethod
    def create_client(cls):
        return _kafka.KafkaClient(settings.KAFKA['URL'])

    @classmethod
    def create_consumer(cls, *topics):
        return cls.Consumer(
            *topics,
            metadata_broker_list=[settings.KAFKA['URL']]
        )

    @classmethod
    def create_producer(cls):
        client = cls.create_client()
        producer = _kafka.SimpleProducer(
            client,
            async=False,
            req_acks=_kafka.SimpleProducer.ACK_AFTER_CLUSTER_COMMIT,
            ack_timeout=3000
        )
        return producer

    class Topic(object):

        def __init__(self, name):
            self.name = name

        def create(self):
            Engine.create_client().ensure_topic_exists(self.name)
            return self

    class Consumer(_kafka.KafkaConsumer):

        def seek(self, topic, partition, offset):
            self._offsets.fetch[(topic, partition)] += offset

        def set_offset(self, topic, partition, offset):
            self._offsets.fetch[(topic, partition)] = offset