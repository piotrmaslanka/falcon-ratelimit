# coding=UTF-8
from __future__ import print_function, absolute_import, division
import datetime, falcon, logging, time, six
from falcon import testing
from falconratelimit import rate_limit
from freezegun import freeze_time

logger = logging.getLogger(__name__)


class NoRedisResource(object):
    @falcon.before(rate_limit(per_second=1, window_size=5))
    def on_post(self, req, resp):
        resp.status = falcon.HTTP_200

class RedisResource(object):
    @falcon.before(rate_limit(redis_url='localhost:6379', per_second=1, window_size=5, resource='on_get'))
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200

app = falcon.API()
app.add_route('/noredis', NoRedisResource())
app.add_route('/redis', RedisResource())


class TestRatelimit(testing.TestCase):
    def setUp(self):
        super(TestRatelimit, self).setUp()
        self.app = app

    def test_limit_ok(self):
        with freeze_time("2018-01-01 00:00:00") as frozen_datetime:
            resp = self.simulate_post('/noredis')
            self.assertEqual(resp.status, falcon.HTTP_200)

            for i in range(4):
                frozen_datetime.tick()
                self.simulate_post('/noredis')

            frozen_datetime.tick()
            resp = self.simulate_post('/noredis')
            self.assertEqual(resp.status, falcon.HTTP_429)

        with freeze_time("2018-01-01 00:00:10") as frozen_datetime:
            resp = self.simulate_post('/noredis')
            self.assertEqual(resp.status, falcon.HTTP_200)

    def test_get_rate_limit(self):
        with freeze_time("2018-01-01 00:00:00") as frozen_datetime:
            resp = self.simulate_get('/redis')
            self.assertEqual(resp.status, falcon.HTTP_200)

            for i in range(4):
                frozen_datetime.tick()
                self.simulate_get('/redis')

            frozen_datetime.tick()
            resp = self.simulate_get('/redis')
            self.assertEqual(resp.status, falcon.HTTP_429)

        with freeze_time("2018-01-01 00:00:10") as frozen_datetime:
            resp = self.simulate_get('/redis')
            self.assertEqual(resp.status, falcon.HTTP_200)