from typing import Type

from propan import PropanApp
from propan.asyncapi.generate import get_app_schema
from propan.broker.core.abc import BrokerUsecase


class SubscriberNamingTestCase:
    broker_class: Type[BrokerUsecase]

    def test_naming(self):
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle_user_created():
            ...

        schema = get_app_schema(PropanApp(broker)).to_jsonable()

        assert tuple(schema["channels"].keys())[0] == "HandleUserCreated"

    def test_naming_manual(self):
        broker = self.broker_class()

        @broker.subscriber("test", title="my_custom_name")
        async def handle_user_created():
            ...

        schema = get_app_schema(PropanApp(broker)).to_jsonable()

        assert tuple(schema["channels"].keys())[0] == "my_custom_name"
