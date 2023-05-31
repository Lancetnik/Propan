import logging
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from aiobotocore.client import AioBaseClient
from aiobotocore.config import AioConfig
from typing_extensions import TypeAlias

from propan.brokers._model import BrokerUsecase
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.push_back_watcher import BaseWatcher
from propan.brokers.sqs.schema import Handler, SQSQueue
from propan.log import access_logger
from propan.types import HandlerWrapper, SendableMessage

T = TypeVar("T")
QueueUrl: TypeAlias = str

class SQSBroker(BrokerUsecase):
    _connection: AioBaseClient
    _queues: Dict[str, QueueUrl]
    handlers: List[Handler]

    def __init__(
        self,
        url: str = "http://localhost:9324/",
        *,
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
    ) -> None:
        """"""
    async def connect(
        self,
        url: str = "http://localhost:9324/",
        *,
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
    async def _connect(self, *args: Any, **kwargs: Any) -> AioBaseClient: ...
    async def close(self) -> None: ...
    async def _parse_message(self, message: Dict[str, Any]) -> PropanMessage: ...
    def _process_message(
        self,
        func: Callable[[PropanMessage], T],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[PropanMessage], T]: ...
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
    ) -> None: ...
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
    ) -> HandlerWrapper: ...
    async def start(self) -> None: ...
    async def create_queue(self, queue: str) -> QueueUrl: ...
    async def delete_queue(self, queue: str) -> None: ...
    async def get_queue(self, queue: str) -> QueueUrl: ...
    async def delete_message(self) -> None: ...
    async def _consume(self, queue_url: str, handler: Handler) -> NoReturn: ...
    @property
    def fmt(self) -> str: ...
    def _get_log_context(  # type: ignore[override]
        self, message: Optional[PropanMessage], queue: str
    ) -> Dict[str, Any]: ...
