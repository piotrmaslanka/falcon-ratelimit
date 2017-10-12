falcon-ratelimit
========
[![Build Status](https://travis-ci.org/piotrmaslanka/falcon-ratelimit.svg)](https://travis-ci.org/piotrmaslanka/falcon-ratelimit)
[![Code Climate](https://codeclimate.com/github/piotrmaslanka/falcon-ratelimit/badges/gpa.svg)](https://codeclimate.com/github/piotrmaslanka/falcon-ratelimit)
[![Issue Count](https://codeclimate.com/github/piotrmaslanka/falcon-ratelimit/badges/issue_count.svg)](https://codeclimate.com/github/piotrmaslanka/falcon-ratelimit)
[![PyPI](https://img.shields.io/pypi/pyversions/falcon-ratelimit.svg)](https://pypi.python.org/pypi/falcon-ratelimit)
[![PyPI version](https://badge.fury.io/py/falcon-ratelimit.svg)](https://badge.fury.io/py/falcon-ratelimit)
[![PyPI](https://img.shields.io/pypi/implementation/falcon-ratelimit.svg)](https://pypi.python.org/pypi/falcon-ratelimit)

Rate limiter for Falcon. Use like:

```python
from falconratelimit import rate_limit
import falcon


class Resource(object):

    @falcon.before(rate_limit(per_second=5, resource='jwt token creation'))
    def on_post(self, req, resp):
        ...

```
