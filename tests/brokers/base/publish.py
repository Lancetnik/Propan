import asyncio
from datetime import datetime
from typing import Dict, List, Tuple
from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from propan.annotations import Logger
from propan.broker.core.abc import BrokerUsecase


class SimpleModel(BaseModel):
    r: str


now = datetime.now()


class BrokerPublishTestcase:
    @pytest.fixture
    def pub_broker(self, full_broker):
        yield full_broker

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("message", "message_type", "expected_message"),
        (
            ("hello", str, None),
            (b"hello", bytes, None),
            (1, int, None),
            (1.0, float, None),
            (False, bool, None),
            ({"m": 1}, Dict[str, int], None),
            ([1, 2, 3], List[int], None),
            (SimpleModel(r="hello!"), SimpleModel, None),
            (SimpleModel(r="hello!"), dict, {"r": "hello!"}),
            (now, datetime, now),
        ),
    )
    async def test_serialize(
        self,
        pub_broker: BrokerUsecase,
        mock: Mock,
        queue: str,
        message,
        message_type,
        expected_message,
    ):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        @pub_broker.subscriber(queue)
        async def handler(m: message_type, logger: Logger):
            mock(m)

        async with pub_broker:
            await pub_broker.start()

            await asyncio.wait(
                (
                    asyncio.create_task(pub_broker.publish(message, queue)),
                    asyncio.create_task(consume.wait()),
                ),
                timeout=3,
            )

        if expected_message is None:
            expected_message = message

        mock.assert_called_with(expected_message)

    @pytest.mark.asyncio
    async def test_unwrap_dict(self, mock: Mock, queue: str, pub_broker: BrokerUsecase):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()

        @pub_broker.subscriber(queue)
        async def m(a: int, b: int, logger: Logger):
            mock({"a": a, "b": b})

        async with pub_broker:
            await pub_broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(pub_broker.publish({"a": 1, "b": 1.0}, queue)),
                    asyncio.create_task(consume.wait()),
                ),
                timeout=3,
            )

        mock.assert_called_with(
            {
                "a": 1,
                "b": 1,
            }
        )

    @pytest.mark.asyncio
    async def test_unwrap_list(self, mock: Mock, queue: str, pub_broker: BrokerUsecase):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()

        @pub_broker.subscriber(queue)
        async def m(a: int, b: int, *args: Tuple[int, ...], logger: Logger):
            mock({"a": a, "b": b, "args": args})

        async with pub_broker:
            await pub_broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(pub_broker.publish([1, 1.0, 2.0, 3.0], queue)),
                    asyncio.create_task(consume.wait()),
                ),
                timeout=3,
            )

        mock.assert_called_with({"a": 1, "b": 1, "args": (2, 3)})

    @pytest.mark.asyncio
    async def test_base_publisher(
        self, mock: Mock, queue: str, pub_broker: BrokerUsecase
    ):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()

        @pub_broker.subscriber(queue)
        @pub_broker.publisher(queue + "resp")
        async def m():
            return ""

        @pub_broker.subscriber(queue + "resp")
        async def resp():
            mock()

        async with pub_broker:
            await pub_broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(pub_broker.publish("", queue)),
                    asyncio.create_task(consume.wait()),
                ),
                timeout=3,
            )

        mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_publisher_object(
        self, mock: Mock, queue: str, pub_broker: BrokerUsecase
    ):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()

        publisher = pub_broker.publisher(queue + "resp")

        @publisher
        @pub_broker.subscriber(queue)
        async def m():
            return ""

        @pub_broker.subscriber(queue + "resp")
        async def resp():
            mock()

        async with pub_broker:
            await pub_broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(pub_broker.publish("", queue)),
                    asyncio.create_task(consume.wait()),
                ),
                timeout=3,
            )

        mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_manual(
        self, mock: Mock, queue: str, pub_broker: BrokerUsecase
    ):
        consume = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()

        publisher = pub_broker.publisher(queue + "resp")

        @pub_broker.subscriber(queue)
        async def m():
            await publisher.publish("")

        @pub_broker.subscriber(queue + "resp")
        async def resp():
            mock()

        async with pub_broker:
            await pub_broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(pub_broker.publish("", queue)),
                    asyncio.create_task(consume.wait()),
                ),
                timeout=3,
            )

        mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_publishers(self, queue: str, pub_broker: BrokerUsecase):
        mock = Mock()
        mock2 = Mock()
        consume = asyncio.Event()
        consume2 = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()
        mock2.side_effect = lambda *_: consume2.set()

        @pub_broker.publisher(queue + "resp2")
        @pub_broker.subscriber(queue)
        @pub_broker.publisher(queue + "resp")
        async def m():
            return ""

        @pub_broker.subscriber(queue + "resp")
        async def resp():
            mock()

        @pub_broker.subscriber(queue + "resp2")
        async def resp():
            mock2()

        async with pub_broker:
            await pub_broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(pub_broker.publish("", queue)),
                    asyncio.create_task(consume.wait()),
                    asyncio.create_task(consume2.wait()),
                ),
                timeout=3,
            )

        mock.assert_called_once()
        mock2.assert_called_once()

    @pytest.mark.asyncio
    async def test_reusable_publishers(self, queue: str, pub_broker: BrokerUsecase):
        mock = Mock()
        consume = asyncio.Event()
        consume2 = asyncio.Event()
        mock.side_effect = lambda *_: consume.set()

        pub = pub_broker.publisher(queue + "resp")

        @pub
        @pub_broker.subscriber(queue)
        async def m():
            return ""

        @pub
        @pub_broker.subscriber(queue + "2")
        async def m():
            return ""

        @pub_broker.subscriber(queue + "resp")
        async def resp():
            if consume.is_set:
                consume2.set()
            else:
                consume.set()
            mock()

        async with pub_broker:
            await pub_broker.start()
            await asyncio.wait(
                (
                    asyncio.create_task(pub_broker.publish("", queue)),
                    asyncio.create_task(pub_broker.publish("", queue + "2")),
                    asyncio.create_task(consume.wait()),
                    asyncio.create_task(consume2.wait()),
                ),
                timeout=3,
            )

        assert consume2.is_set
        assert consume.is_set
        assert mock.call_count == 2
