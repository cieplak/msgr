from tests import TestCase
import uuid

from msgr.brokers import rabbitmq as rabbit


class TestRabbitMQ(TestCase):

    def setUp(self):
        self.queue = rabbit.Engine.Queue('entity_event', 'entity', 'entity.event', True)
        self.deferred_queue_name = self.queue.name + '_deferred'
        rabbit.Engine.create_exchanges()
        rabbit.Engine.create_queue(self.queue)
        rabbit.Engine.Consumer.registry = []
        self.consumer = rabbit.Engine.Consumer()
        self.log = []
        self.messages = [dict(guid=uuid.uuid4().hex) for _ in xrange(3)]

    def tearDown(self):
        rabbit.Engine.delete_queue(self.queue.name)
        rabbit.Engine.delete_queue(self.deferred_queue_name)

    def publish_msg(self, payload):
        return rabbit.send(
            key=self.queue.routing_key,
            payload=payload
        )

    def test_pubsub(self):
        @rabbit.receive(self.queue.name)
        def process_event(payload):
            self.log.append(payload)

        map(self.publish_msg, self.messages)
        list(self.consumer.consume(limit=len(self.messages)))
        self.assertEqual(sorted(self.messages), sorted(self.log))

    def test_deferred_queue(self):
        @rabbit.receive(self.queue.name)
        def process_event(payload):
            raise

        @rabbit.receive(self.deferred_queue_name)
        def log_deferred_msg(payload):
            self.log.append(payload)

        map(self.publish_msg, self.messages)
        list(self.consumer.consume(limit=len(self.messages * 2)))
        self.assertEqual(sorted(self.messages), sorted(self.log))

    def test_deferred_msgs_are_deadlettered_to_primary_queue(self):
        rabbit.Engine.delete_queue(self.deferred_queue_name)
        rabbit.Engine.create_queue(self.queue, retry_delay=1)

        @rabbit.receive(self.queue.name)
        def process_event(payload):
            self.log.append(payload)
            raise

        map(self.publish_msg, self.messages)
        list(self.consumer.consume(limit=len(self.messages * 2)))
        self.assertEqual(sorted(self.messages * 2), sorted(self.log))