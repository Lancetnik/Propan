import asyncio
import logging
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from aiobotocore.client import AioBaseClient
from aiobotocore.config import AioConfig
from fast_depends.dependencies import Depends
from typing_extensions import TypeAlias

from propan.brokers._model import BrokerAsyncUsecase
from propan.brokers._model.broker_usecase import (
    AsyncDecoder,
    AsyncParser,
    HandlerCallable,
    T_HandlerReturn,
)
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.middlewares import BaseMiddleware
from propan.brokers.push_back_watcher import BaseWatcher
from propan.brokers.sqs.schema import Handler, SQSQueue
from propan.log import access_logger
from propan.types import AnyDict, DecodedMessage, SendableMessage

T = TypeVar("T")
QueueUrl: TypeAlias = str
SQSMessage: TypeAlias = PropanMessage[AnyDict]

class SQSBroker(BrokerAsyncUsecase[AnyDict, AioBaseClient]):
    _queues: Dict[str, QueueUrl]
    response_queue: str
    middlewares: Sequence[Type[BaseMiddleware[AnyDict]]]
    response_callbacks: Dict[str, "asyncio.Future[DecodedMessage]"]
    handlers: List[Handler]

    def __init__(
        self,
        url: str = "http://localhost:9324/",
        *,
        response_queue: str = "",
        region_name: Optional[str] = None,
        api_version: Optional[str] = None,
        use_ssl: bool = True,
        verify: Optional[bool] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        config: Optional[AioConfig] = None,
        # broker
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
        dependencies: Sequence[Depends] = (),
        middlewares: Sequence[Type[BaseMiddleware[AnyDict]]] = (),
        decode_message: AsyncDecoder[AnyDict] = None,
        parse_message: AsyncParser[AnyDict] = None,
        protocol: str = "sqs",
    ) -> None:
        """"""
    async def connect(
        self,
        *,
        url: str = "http://localhost:9324/",
        region_name: Optional[str] = None,
        api_version: Optional[str] = None,
        use_ssl: bool = True,
        verify: Optional[bool] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        config: Optional[AioConfig] = None,
    ) -> AioBaseClient:
        """"""
    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        """"""
    async def publish(  # type: ignore[override]
        self,
        message: SendableMessage,
        queue: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        delay_seconds: int = 0,
        message_attributes: Optional[Dict[str, Any]] = None,
        message_system_attributes: Optional[Dict[str, Any]] = None,
        deduplication_id: Optional[str] = None,
        group_id: Optional[str] = None,
        reply_to: str = "",
        callback: bool = False,
        callback_timeout: Optional[float] = None,
        raise_timeout: bool = False,
    ) -> None:
        """"""
    def handle(  # type: ignore[override]
        self,
        queue: Union[str, SQSQueue],
        *,
        wait_interval: int = 1,
        max_messages_number: int = 10,  # 1...10
        attributes: Sequence[str] = (),
        message_attributes: Sequence[str] = (),
        request_attempt_id: Optional[str] = None,
        visibility_timeout: int = 0,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: AsyncDecoder[AnyDict] = None,
        parse_message: AsyncParser[AnyDict] = None,
        description: str = "",
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[AnyDict, bool], Awaitable[T_HandlerReturn]],
    ]:
        """"""
    async def start(self) -> None:
        """"""
    async def create_queue(self, queue: str) -> QueueUrl:
        """"""
    async def delete_queue(self, queue: str) -> None:
        """"""
    async def get_queue(self, queue: str) -> QueueUrl:
        """"""
    async def delete_message(self) -> None:
        """"""
    async def _consume(self, queue_url: str, handler: Handler) -> NoReturn: ...
    @property
    def fmt(self) -> str: ...
    def _get_log_context(  # type: ignore[override]
        self, message: Optional[SQSMessage], queue: str
    ) -> Dict[str, Any]: ...
    @classmethod
    def _build_message(
        cls,
        message: SendableMessage,
        queue_url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        delay_seconds: int = 0,  # 0...900
        message_attributes: Optional[Dict[str, Any]] = None,
        message_system_attributes: Optional[Dict[str, Any]] = None,
        # FIFO only
        deduplication_id: Optional[str] = None,
        group_id: Optional[str] = None,
        # broker
        reply_to: str = "",
    ) -> Dict[str, Any]: ...
    async def _parse_message(self, message: Dict[str, Any]) -> SQSMessage: ...
    def _process_message(
        self,
        func: Callable[[SQSMessage], T],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[SQSMessage], T]: ...
    async def _connect(self, *args: Any, **kwargs: Any) -> AioBaseClient: ...
