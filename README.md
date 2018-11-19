falcon-ratelimit
========

[![Build Status](https://travis-ci.org/piotrmaslanka/falcon-ratelimit.svg)](https://travis-ci.org/piotrmaslanka/falcon-ratelimit)
[![Maintainability](https://api.codeclimate.com/v1/badges/698296b5954d7cbdd0dc/maintainability)](https://codeclimate.com/github/piotrmaslanka/falcon-ratelimit/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/698296b5954d7cbdd0dc/test_coverage)](https://codeclimate.com/github/piotrmaslanka/falcon-ratelimit/test_coverage)
[![Issue Count](https://codeclimate.com/github/piotrmaslanka/falcon-ratelimit/badges/issue_count.svg)](https://codeclimate.com/github/piotrmaslanka/falcon-ratelimit)
[![PyPI](https://img.shields.io/pypi/pyversions/falcon-ratelimit.svg)](https://pypi.python.org/pypi/falcon-ratelimit)
[![PyPI version](https://badge.fury.io/py/falcon-ratelimit.svg)](https://badge.fury.io/py/falcon-ratelimit)
[![PyPI](https://img.shields.io/pypi/implementation/falcon-ratelimit.svg)](https://pypi.python.org/pypi/falcon-ratelimit)

Rate limiter for Falcon. Use like:

```python
import falcon
from falconratelimit import rate_limit


class NoRedisResource(object):
    @falcon.before(rate_limit(per_second=5, window_size=30 resource='resource_name'))
    def on_post(self, req, resp):
        ...

class RedisResource(object):
   @falcon.before(rate_limit(redis_url='localhost:6379', per_second=1, window_size=10))
   def on_post(self, req, resp):
       ...
```

This package works by limiting the number of requests using two variables `per_second` and `window_size`. In the first example above, the `NoRedisResource` class is restricted to 5 requests per second over a 30 second window meaning that there is a limit of 150 requests over 30 seconds. The default storage of calling the `rate_limit` decorator is an in memory list to store the number of requests for the given user using the resource `resource_name`.

The second example implements the optional storage to use Redis by passing in a `redis_url` to store user request data. Using Redis allows for the rate limiting to be implemented across multiple instances of a particular application. In the `RedisResource` class example the user is allowed to make 1 request per second over 10 seconds meaning that there is a limit of 10 requests over 10 seconds. Since this example didn't pass in a `resource` it uses `default` as the name for request storage.