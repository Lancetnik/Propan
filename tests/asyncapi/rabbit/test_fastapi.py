from propan.rabbit.fastapi import RabbitRouter
from tests.asyncapi.base.arguments import FastAPICompatible
from tests.asyncapi.base.publisher import PublisherTestcase


class TestRouterArguments(FastAPICompatible):
    broker_class = RabbitRouter

    def build_app(self, router):
        return router


class TestRouterPublisher(PublisherTestcase):
    broker_class = RabbitRouter

    def build_app(self, router):
        return router
