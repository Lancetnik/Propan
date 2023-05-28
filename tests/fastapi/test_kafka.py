from propan.fastapi import KafkaRouter
from propan.test import TestKafkaBroker
from tests.fastapi.case import FastAPITestcase


class TestKafkaRouter(FastAPITestcase):
    router_class = KafkaRouter
    broker_test = staticmethod(TestKafkaBroker)
