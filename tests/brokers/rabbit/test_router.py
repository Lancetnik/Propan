import pytest

from tests.brokers.base.router import RouterLocalTestcase, RouterTestcase


@pytest.mark.rabbit
class TestRabbitRouter(RouterTestcase):
    pass


class TestRabbitRouterLocal(RouterLocalTestcase):
    pass
