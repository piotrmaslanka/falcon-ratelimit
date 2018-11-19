# coding=UTF-8
from __future__ import print_function, absolute_import, division

import collections
import falcon
import functools
import logging
import warnings

try:
    import redis
except ImportError:
    warnings.warn('redis module not installed')
import six
import time

logger = logging.getLogger(__name__)

Argument = collections.namedtuple('Argument', ('resource', 'window_size',
                                               'per_second', 'error_message',
                                               'redis_url'))

try:
    redis
except NameError:
    pass
else:
    class _RateLimitDBRedis(object):
        @staticmethod
        def filter(user, resource_name, window_size, broker):
            key_name = str(user + resource_name)
            p = broker.smembers(key_name)
            t = time.time()
            exp_time = t - window_size
            expired_values = [s for s in p if float(s) < exp_time]
            for value in expired_values:
                broker.srem(key_name, value)

        @staticmethod
        def add_call(user, resource_name, broker):
            broker.sadd(user + resource_name, time.time())

        @staticmethod
        def check_for(user, argument, broker):
            _RateLimitDBRedis.filter(user, argument.resource,
                                     argument.window_size, broker)
            _RateLimitDBRedis.add_call(user, argument.resource, broker)
            times_called = len(broker.smembers(user + argument.resource))
            return (times_called / argument.window_size) > argument.per_second


class _RateLimitDB(object):
    _RATE_LIMIT_DB = collections.defaultdict(
        lambda: collections.defaultdict(list)
    )

    @staticmethod
    def filter(user, resource_name, window_size):
        p = _RateLimitDB._RATE_LIMIT_DB[user][resource_name]
        t = time.time()
        exp_int = t - window_size
        p = [s for s in p if s >= exp_int]
        _RateLimitDB._RATE_LIMIT_DB[user][resource_name] = p

    @staticmethod
    def add_call(user, resource_name):
        _RateLimitDB._RATE_LIMIT_DB[user][resource_name].append(
            time.time()
        )

    @staticmethod
    def check_for(user, argument):
        _RateLimitDB.filter(user, argument.resource, argument.window_size)
        _RateLimitDB.add_call(user, argument.resource)
        p = len(_RateLimitDB._RATE_LIMIT_DB[user][argument.resource])
        return (p / window_size) > argument.per_second


def _rate_db(req, resp, argument):
    if _RateLimitDB.check_for(req.forwarded_host, argument):
        resp.status = falcon.HTTP_429
        raise falcon.HTTPTooManyRequests(argument.error_message)


def _rate_redis(req, resp, argument):
    broker = redis.StrictRedis.from_url(argument.redis_url)
    if _RateLimitDBRedis.check_for(req.forwarded_host, argument, broker):
        resp.status = falcon.HTTP_429
        raise falcon.HTTPTooManyRequests(argument.error_message)


def rate_limit(per_second=30, resource=u'default', window_size=10,
               error_message="429 Too Many Requests",
               redis_url=None):
    def hook(req, resp, params):
        if redis_url:
            try:
                redis
            except NameError:
                raise ValueError(
                    'Cannot use redis - no redis module installed!')
            else:
                _rate_redis(req, resp, Argument(resource, window_size,
                                                per_second, error_message,
                                                redis_url))
        else:
            _rate_db(req, resp, Argument(resource, window_size, per_second,
                                         error_message, None))

    return hook
