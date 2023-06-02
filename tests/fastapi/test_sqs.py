from propan.fastapi import SQSRouter
from propan.test import TestSQSBroker
from tests.fastapi.case import FastAPITestcase


class TestSQSRouter(FastAPITestcase):
    router_class = SQSRouter
    broker_test = staticmethod(TestSQSBroker)
