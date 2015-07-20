from tests import TestCase
import uuid

from msgr.brokers import kafka


class TestKafka(TestCase):

    topic = 'price.changed'

    def setUp(self):
        self.topic = kafka.Engine.Topic(self.topic).create()
        self.log = []
        self.messages = [dict(guid=uuid.uuid4().hex) for _ in xrange(3)]

    def test_pubsub(self):
        @kafka.receive(self.topic.name)
        def process_event(payload):
            self.log.append(payload)

        for message in self.messages:
            kafka.send(topic=self.topic.name, message=message)
        consumer = kafka.Engine.create_consumer(self.topic.name)
        consumer.seek(self.topic.name, 0, -len(self.messages))
        kafka.process(limit=len(self.messages), consumer=consumer)
        self.assertEqual(sorted(self.messages), sorted(self.log))
