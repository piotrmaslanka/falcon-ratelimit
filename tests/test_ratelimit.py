# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import falcon
from falcon import testing
from falconratelimit import get_rate_limit_hook, rate_limit
import time

logger = logging.getLogger(__name__)


class Resource(object):
    @falcon.before(rate_limit(per_second=3, window_size=5))
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200

    @falcon.before(get_rate_limit_hook('http://example.com', per_second=3, window_size=5))
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200

app = falcon.API()
app.add_route('/', Resource())


class TestRatelimit(testing.TestCase):

    def setUp(self):
        super(TestRatelimit, self).setUp()
        self.app = app

    def test_limit_ok(self):
        resp = self.simulate_post('/')
        self.assertEqual(resp.status, falcon.HTTP_200)

        for i in range(16):
            self.simulate_post('/')

        resp = self.simulate_post('/')
        self.assertEqual(resp.status, falcon.HTTP_429)

        time.sleep(6)

        resp = self.simulate_post('/')
        self.assertEqual(resp.status, falcon.HTTP_200)

    def test_get_rate_limit(self):
        resp = self.simulate_get('/')
        self.assertEqual(resp.status, falcon.HTTP_200)

        for i in range(16):
            self.simulate_get('/')

        resp = self.simulate_get('/')
        self.assertEqual(resp.status, falcon.HTTP_429)

        time.sleep(6)

        resp = self.simulate_get('/')
        self.assertEqual(resp.status, falcon.HTTP_200)