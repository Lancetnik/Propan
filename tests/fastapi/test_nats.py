from propan.fastapi import NatsRouter
from propan.test import TestNatsBroker
from tests.fastapi.case import FastAPITestcase


class TestNatsRouter(FastAPITestcase):
    router_class = NatsRouter
    broker_test = staticmethod(TestNatsBroker)
