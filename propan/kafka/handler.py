import asyncio
from typing import Any, AsyncContextManager, Awaitable, Callable, List, Optional

import anyio
from aiokafka import AIOKafkaConsumer, ConsumerRecord
from fast_depends.core import CallModel
from typing_extensions import Never

from propan.broker.handler import AsyncHandler
from propan.broker.types import (
    AsyncCustomDecoder,
    AsyncCustomParser,
    AsyncWrappedHandlerCall,
    P_HandlerParams,
    T_HandlerReturn,
)
from propan.broker.wrapper import HandlerCallWrapper
from propan.kafka.message import KafkaMessage
from propan.kafka.parser import AioKafkaParser
from propan.types import AnyDict


class LogicHandler(AsyncHandler[ConsumerRecord]):
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

    # TODO: use **kwargs: Unpack[ConsumerConnectionParams] with py3.12 release 2023-10-02
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
        handler: HandlerCallWrapper[ConsumerRecord, P_HandlerParams, T_HandlerReturn],
        wrapped_call: AsyncWrappedHandlerCall[ConsumerRecord, T_HandlerReturn],
        dependant: CallModel[P_HandlerParams, T_HandlerReturn],
        parser: Optional[AsyncCustomParser[ConsumerRecord]] = None,
        decoder: Optional[AsyncCustomDecoder[ConsumerRecord]] = None,
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
