from __future__ import absolute_import
from collections import namedtuple
from functools import partial
import logging

import redis as _redis


logger = logging.getLogger(__name__)
PubSubCache = None


def init(config):
    global PubSubCache
    Cache = partial(_redis.StrictRedis,
                    host=config.REDIS['HOST'],
                    port=config.REDIS['PORT'],
                    socket_timeout=config.REDIS['SOCKET_TIMEOUT'],
                    )
    PubSubCache = Cache(db=config.REDIS['PUBSUB_DB'])


def send(channel, message):
    PubSubCache.publish(channel, message)


def receive(channel):
    def outer(inner):
        subscriber = Engine.Subscriber(func=inner, channel=channel)
        Engine.register(subscriber)
        return inner
    return outer


def process(*args, **kwargs):
    callback_by_channel = {
        s.channel: s.func
        for s in Engine.subscribers
    }
    mq = PubSubCache.pubsub()
    map(mq.subscribe, callback_by_channel)
    for raw_message in mq.listen():
        try:
            func = callback_by_channel[raw_message.get('channel')]
            func(raw_message['message'])
        except KeyError:
            logger.warning('No subscriber for %s' % raw_message.get('channel'))


class Engine(object):

    subscribers = set()

    Subscriber = namedtuple('Subscriber', [
        'channel',
        'func',
        ])

    @classmethod
    def register(cls, subscriber):
        Engine.subscribers.add(subscriber)