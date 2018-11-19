# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six, logging, functools, collections, time, falcon, redis

logger = logging.getLogger(__name__)


class AbstractRateLimitDB(object):
    def filter():
        raise NotImplementedError

    def add_call():
        raise NotImplementedError

    def check_for():
        raise NotImplementedError


class _RateLimitDBRedis(AbstractRateLimitDB):
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
    def check_for(user, resource_name, window_size, broker):
        _RateLimitDBRedis.filter(user, resource_name, window_size, broker)
        _RateLimitDBRedis.add_call(user, resource_name, broker)
        times_called = len(broker.smembers(user + resource_name))
        return times_called / window_size



class _RateLimitDB(AbstractRateLimitDB):
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
    def check_for(user, resource_name, window_size):
        _RateLimitDB.filter(user, resource_name, window_size)
        _RateLimitDB.add_call(user, resource_name)
        p = len(_RateLimitDB._RATE_LIMIT_DB[user][resource_name])
        return p / window_size


def rate_limit(per_second=30, resource=u'default', window_size=10, error_message="429 Too Many Requests", redis_url=None):
    def hook(req, resp, params):
        if redis_url:
            broker = redis.StrictRedis.from_url(redis_url)
            if _RateLimitDBRedis.check_for(req.forwarded_host,
                                    resource,
                                    window_size, broker) > per_second:
                resp.status = falcon.HTTP_429
                raise falcon.HTTPTooManyRequests(error_message)
        else:
            if _RateLimitDB.check_for(req.forwarded_host,
                                    resource,
                                    window_size) > per_second:
                resp.status = falcon.HTTP_429
                raise falcon.HTTPTooManyRequests(error_message)
    return hook
