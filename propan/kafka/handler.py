import asyncio
from typing import Any, AsyncContextManager, Awaitable, Callable, List, Optional

import anyio
from aiokafka import AIOKafkaConsumer, ConsumerRecord
from fast_depends.core import CallModel
from typing_extensions import Never

from propan.broker.handler import AsyncHandler
from propan.broker.schemas import HandlerCallWrapper
from propan.broker.types import AsyncDecoder, AsyncParser
from propan.kafka.helpers import AioKafkaParser
from propan.kafka.message import KafkaMessage
from propan.types import AnyDict, F_Return, F_Spec


class Handler(AsyncHandler[ConsumerRecord]):
    topics: List[str]

    consumer: Optional[AIOKafkaConsumer] = None
    task: Optional["asyncio.Task[Any]"] = None

    def __init__(
        self,
        *topics,
        # Kafka information
        builder: Callable[[], AIOKafkaConsumer],
        # AsyncAPI information
        description: Optional[str] = None,
    ):
        super().__init__(
            description=description,
        )

        self.topics = topics
        self.builder = builder
        self.task = None
        self.consumer = None

    async def start(self, **consumer_kwargs: AnyDict) -> None:
        self.consumer = consumer = self.builder(*self.topics, **consumer_kwargs)
        await consumer.start()
        self.task = asyncio.create_task(self._consume())

    async def close(self) -> None:
        if self.consumer is not None:
            await self.consumer.stop()
            self.consumer = None

        if self.task is not None:
            self.task.cancel()
            self.task = None

    def add_call(
        self,
        handler: HandlerCallWrapper[F_Spec, F_Return],
        wrapped_call: Callable[
            [KafkaMessage, bool],
            Awaitable[Optional[F_Return]],
        ],
        dependant: CallModel[F_Spec, F_Return],
        parser: Optional[AsyncParser[ConsumerRecord]] = None,
        decoder: Optional[AsyncDecoder[ConsumerRecord]] = None,
        filter: Callable[
            [KafkaMessage], Awaitable[bool]
        ] = lambda m: not m.processed,  # pragma: no cover
        middlewares: Optional[
            List[Callable[[KafkaMessage], AsyncContextManager[None]]]
        ] = None,
    ) -> None:
        super().add_call(
            handler=handler,
            wrapped_call=wrapped_call,
            parser=self._resolve_custom_func(parser, AioKafkaParser.parse_message),
            decoder=self._resolve_custom_func(decoder, AioKafkaParser.decode_message),
            filter=filter,
            dependant=dependant,
            middlewares=middlewares,
        )

    async def _consume(self) -> Never:
        # TODO: log connection lost
        # c = self._get_log_context(None, self.topics)

        connected = True
        while True:
            try:
                msg = await self.consumer.getone()

            except Exception:
                if connected is True:
                    # self._log(e, logging.WARNING, c)
                    connected = False
                await anyio.sleep(5)

            else:
                if connected is False:
                    # self._log("Connection established", logging.INFO, c)
                    connected = True

                await self.consume(msg)
