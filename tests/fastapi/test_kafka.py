from propan.fastapi import KafkaRouter
from propan.test.kafka import TestKafkaBroker, build_message
from tests.fastapi.case import FastAPITestcase


class TestKafkaRouter(FastAPITestcase):
    router_class = KafkaRouter
    broker_test = staticmethod(TestKafkaBroker)
    build_message = staticmethod(build_message)
