# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import functools
import collections
import time
import falcon

logger = logging.getLogger(__name__)


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
    def check_for(user, resource_name, window_size):
        _RateLimitDB.filter(user, resource_name, window_size)
        _RateLimitDB._RATE_LIMIT_DB[user][resource_name].append(time.time())
        return len(_RateLimitDB._RATE_LIMIT_DB[user][resource_name]) / window_size


def rate_limit(per_second=30, resource=u'', window_size=10):
    def hook(req, resp, resource, params):
        if _RateLimitDB.check_for(req.forwarded_host, resource, window_size) > per_second:
            raise falcon.HTTPTooManyRequests('Rate limited')
    return hook
