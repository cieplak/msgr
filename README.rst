msgr
----

broker agnostic messaging for python

currently supports the following backends:

 - kafka
 - rabbitmq
 - redis

Usage
-----

.. code:: python


    from msgr import Message
    from msgr.brokers import kafka, rabbitmq

    from my_app import Entity

    channel = '/entities'

    msg = Message(
        channel=channel,
        body=dict(guid='OR-hWfPTYiLekYfErUncmngiL'),
    )

    kafka.send(msg)
    rabbitmq.send(msg)

    def propagate_entity_changes(message):
        entity = Entity(**message)
        entity.save()

    kafka.receive(channel)(propagate_entity_changes)
    rabbit.receive(channel)(propagate_entity_changes)

    kafka.ingest(limit=2)
    rabbit.ingest(limit=2)



Command Line Usage
------------------

Start an interactive msgr shell:

.. code:: base

    msgr shell

Start a message consumer with 10 workers:

.. code:: python

    msgr consume --concurrency 10

