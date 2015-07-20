from __future__ import absolute_import
from functools import partial

import redis as _redis


LogCache = None


def init(config):
    global LogCache
    apply_params = lambda client: partial(
        client,
        host=config.REDIS['HOST'],
        port=config.REDIS['PORT'],
        socket_timeout=config.REDIS['SOCKET_TIMEOUT'],
    )
    log_cache = apply_params(_LogCache)
    LogCache = log_cache(db=config.REDIS['LOG_DB'])


class _LogCache(_redis.StrictRedis):

    @classmethod
    def log(cls, entity_guid, event_enum_value):
        return cls.lpush(entity_guid, event_enum_value)

    @classmethod
    def logs_for(cls, entity_guid, event_enum_value=None):
        logs = cls.lrange(entity_guid, 0, -1)
        if event_enum_value:
            logs = [l for l in logs if l == event_enum_value]
        return logs
