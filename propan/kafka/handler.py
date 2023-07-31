import asyncio
from typing import Any, AsyncContextManager, Awaitable, Callable, List, Optional

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from fast_depends.core import CallModel

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
        self.consumer = consumer = self.builder(**consumer_kwargs)
        await consumer.start()

    async def close(self) -> None:
        if self.consumer is not None:
            await self.consumer.stop()
            self.consumer = None

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
