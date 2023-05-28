from propan.fastapi import RedisRouter
from propan.test import TestRedisBroker
from tests.fastapi.case import FastAPITestcase


class TestRedisRouter(FastAPITestcase):
    router_class = RedisRouter
    broker_test = staticmethod(TestRedisBroker)
