from propan.fastapi import SQSRouter
from propan.test.sqs import TestSQSBroker, build_message
from tests.fastapi.case import FastAPITestcase


class TestSQSRouter(FastAPITestcase):
    router_class = SQSRouter
    broker_test = staticmethod(TestSQSBroker)
    build_message = staticmethod(build_message)
