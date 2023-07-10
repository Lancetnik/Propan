import pytest

from propan.test.sqs import build_message
from tests.brokers.base.middlewares import MiddlewareTestCase


@pytest.mark.sqs
class TestSQSMiddleware(MiddlewareTestCase):
    build_message = staticmethod(build_message)
