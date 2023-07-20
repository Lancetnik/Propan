import asyncio
from unittest.mock import Mock

import pytest

from propan.broker.core.asyncronous import BrokerAsyncUsecase
from propan.broker.router import BrokerRouter
from propan.types import AnyCallable


@pytest.mark.asyncio
class RouterTestcase:
    build_message: AnyCallable

    @pytest.fixture
    def pub_broker(self, broker):
        return broker

    async def test_empty_prefix(
        self,
        mock: Mock,
        router: BrokerRouter,
        pub_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        @router.subscriber(queue)
        def subscriber():
            mock()

        pub_broker.include_router(router)

        await pub_broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(pub_broker.publish("hello", queue)),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        mock.assert_called_once()

    async def test_not_empty_prefix(
        self,
        mock: Mock,
        router: BrokerRouter,
        pub_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        router.prefix = "test_"

        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        @router.subscriber(queue)
        def subscriber():
            mock()

        pub_broker.include_router(router)

        await pub_broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(pub_broker.publish("hello", f"test_{queue}")),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        mock.assert_called_once()

    async def test_empty_prefix_publisher(
        self,
        mock: Mock,
        router: BrokerRouter,
        pub_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        @router.subscriber(queue)
        @router.publisher(queue + "resp")
        def subscriber():
            return "hi"

        @router.subscriber(queue + "resp")
        def response():
            mock()

        pub_broker.include_router(router)

        await pub_broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(pub_broker.publish("hello", queue)),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        mock.assert_called_once()

    async def test_not_empty_prefix_publisher(
        self,
        mock: Mock,
        router: BrokerRouter,
        pub_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        router.prefix = "test_"

        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        @router.subscriber(queue)
        @router.publisher(queue + "resp")
        def subscriber():
            return "hi"

        @router.subscriber(queue + "resp")
        def response():
            mock()

        pub_broker.include_router(router)

        await pub_broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(pub_broker.publish("hello", f"test_{queue}")),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        mock.assert_called_once()

    async def test_manual_publisher(
        self,
        mock: Mock,
        router: BrokerRouter,
        pub_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        router.prefix = "test_"

        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        p = router.publisher(queue + "resp")

        @router.subscriber(queue)
        async def subscriber():
            await p.publish("resp")

        @router.subscriber(queue + "resp")
        def response():
            mock()

        pub_broker.include_router(router)

        await pub_broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(pub_broker.publish("hello", f"test_{queue}")),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        mock.assert_called_once()


@pytest.mark.asyncio
class RouterLocalTestcase(RouterTestcase):
    @pytest.fixture
    def pub_broker(self, test_broker):
        return test_broker

    async def test_publisher_mock(
        self,
        router: BrokerRouter,
        pub_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        consume = asyncio.Event()

        pub = router.publisher(queue + "resp")

        @router.subscriber(queue)
        @pub
        def subscriber():
            consume.set()
            return "hi"

        pub_broker.include_router(router)

        await pub_broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(pub_broker.publish("hello", queue)),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        pub.mock.assert_called_with("hi")

    async def test_subscriber_mock(
        self,
        router: BrokerRouter,
        pub_broker: BrokerAsyncUsecase,
        queue: str,
    ):
        consume = asyncio.Event()

        @router.subscriber(queue)
        def subscriber():
            consume.set()
            return "hi"

        pub_broker.include_router(router)

        await pub_broker.start()

        await asyncio.wait(
            (
                asyncio.create_task(pub_broker.publish("hello", queue)),
                asyncio.create_task(consume.wait()),
            ),
            timeout=3,
        )

        subscriber.mock.assert_called_with("hello")

    async def test_manual_publisher_mock(
        self, queue: str, pub_broker: BrokerAsyncUsecase
    ):
        publisher = pub_broker.publisher(queue + "resp")

        @pub_broker.subscriber(queue)
        async def m():
            await publisher.publish("response")

        await pub_broker.start()
        await pub_broker.publish("hello", queue)
        publisher.mock.assert_called_with("response")
