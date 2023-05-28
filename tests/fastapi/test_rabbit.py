from propan.fastapi import RabbitRouter
from propan.test import TestRabbitBroker
from tests.fastapi.case import FastAPITestcase


class TestRabbitRouter(FastAPITestcase):
    router_class = RabbitRouter
    broker_test = staticmethod(TestRabbitBroker)
