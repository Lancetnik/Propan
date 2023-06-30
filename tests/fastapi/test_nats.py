from propan.fastapi import NatsRouter
from propan.test.nats import TestNatsBroker, build_message
from tests.fastapi.case import FastAPITestcase


class TestNatsRouter(FastAPITestcase):
    router_class = NatsRouter
    broker_test = staticmethod(TestNatsBroker)
    build_message = staticmethod(build_message)
