from propan.rabbit.fastapi import RabbitRouter
from propan.rabbit.test import TestRabbitBroker, build_message
from tests.brokers.base.fastapi import FastAPITestcase


class TestRabbitRouter(FastAPITestcase):
    router_class = RabbitRouter
    broker_test = staticmethod(TestRabbitBroker)
    build_message = staticmethod(build_message)
