from propan.fastapi import RedisRouter
from propan.test.redis import TestRedisBroker, build_message
from tests.fastapi.case import FastAPITestcase


class TestRedisRouter(FastAPITestcase):
    router_class = RedisRouter
    broker_test = staticmethod(TestRedisBroker)
    build_message = staticmethod(build_message)
