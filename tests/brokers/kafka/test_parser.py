import pytest

from propan.kafka import KafkaBroker
from tests.brokers.base.parser import CustomParserTestcase


@pytest.mark.kafka
class TestCustomParser(CustomParserTestcase):
    broker_class = KafkaBroker
