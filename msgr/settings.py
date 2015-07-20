from __future__ import unicode_literals


AMQP = dict(
    EXCHANGE='exchange',
    DEFERRED_EXCHANGE='exchange_deferred',
    DLX_EXCHANGE='exchange_dlx',
    IP_ADDRESS='0.0.0.0',
    PORT=5672,
    USER='guest',
    PASSWORD='guest',

    QUEUES=[
        # (queue, exchange, routing_key, should_retry)
    ],
)

AMQP['URI'] = 'amqp://{user}:{password}@{host}:{port}/'.format(
    user=AMQP['USER'],
    password=AMQP['PASSWORD'],
    host=AMQP['IP_ADDRESS'],
    port=AMQP['PORT'],
)

REDIS = dict(
    HOST='0.0.0.0',
    PORT='26379',
    SOCKET_TIMEOUT=5,
    LOG_DB=0,  # TODO
    PUBSUB_DB=0,  # TODO
)

KAFKA = dict(
    URL='0.0.0.0:9092'
)

ZK = dict(
    URL='0.0.0.0:2181'
)

ES = dict(
    URL='0.0.0.0:9300'
)
