

class Broker(object):
    """
    Message broker interface
    """
    def send(self, message):
        """
        Send a message to the broker
        """
        raise NotImplementedError()

    def receive(self, *args, **kwargs):
        """
        A decorator for wrapping functions that wish to receive messages from
        the broker, generally along with some parameters such as a queue name,
        routing key, topic, filter, channel, partition, etc.
        You can put these all around your code and they will be registered
        upon message ingestion initiation.
        """
        raise NotImplementedError()

    def process(self, *args, **kwargs):
        """
        Connect to the message broker and forward messages to the `receive`
        endpoints in the application
        """
        raise NotImplementedError()

    class Engine(object):
        """
        Operations specific to the broker engine
        """
        pass



from . import kafka, rabbitmq, redis
