import logging
from ssl import SSLContext
from types import TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

import aio_pika
import aiormq
from aio_pika.message import IncomingMessage
from fast_depends.dependencies import Depends
from pamqp.common import FieldTable
from typing_extensions import TypeAlias
from yarl import URL

from propan.brokers._model import BrokerAsyncUsecase
from propan.brokers._model.broker_usecase import AsyncDecoder, AsyncParser
from propan.brokers._model.schemas import PropanMessage
from propan.brokers.middlewares import BaseMiddleware
from propan.brokers.push_back_watcher import BaseWatcher
from propan.brokers.rabbit.schemas import Handler, RabbitExchange, RabbitQueue
from propan.log import access_logger
from propan.types import AnyDict, DecodedMessage, SendableMessage

PikaSendableMessage: TypeAlias = Union[aio_pika.message.Message, SendableMessage]
T_HandlerReturn = TypeVar("T_HandlerReturn", bound=PikaSendableMessage)
HandlerCallable: TypeAlias = Callable[
    ..., Union[T_HandlerReturn, Awaitable[T_HandlerReturn]]
]

RabbitMessage: TypeAlias = PropanMessage[IncomingMessage]

class RabbitBroker(BrokerAsyncUsecase[IncomingMessage, aio_pika.RobustConnection]):
    handlers: List[Handler]
    middlewares: Sequence[Type[BaseMiddleware[IncomingMessage]]]
    _channel: Optional[aio_pika.RobustChannel]

    __max_queue_len: int
    __max_exchange_len: int

    def __init__(
        self,
        url: Union[str, URL, None] = None,
        *,
        host: str = "localhost",
        port: int = 5672,
        login: str = "guest",
        password: str = "guest",
        virtualhost: str = "/",
        ssl: bool = False,
        ssl_options: Optional[aio_pika.abc.SSLOptions] = None,
        ssl_context: Optional[SSLContext] = None,
        timeout: aio_pika.abc.TimeoutType = None,
        client_properties: Optional[FieldTable] = None,
        # broker
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
        consumers: Optional[int] = None,
        dependencies: Sequence[Depends] = (),
        middlewares: Sequence[Type[BaseMiddleware[IncomingMessage]]] = (),
        decode_message: AsyncDecoder[IncomingMessage] = None,
        parse_message: AsyncParser[IncomingMessage] = None,
        # AsyncAPI
        protocol: str = "amqp",
        protocol_version: str = "0.9.1",
    ) -> None:
        """RabbitMQ Propan broker

        URL string might be contain ssl parameters e.g.
        `amqps://user:pass@host:port/vhost?ca_certs=ca.pem&certfile=crt.pem&keyfile=key.pem`

        Args:
            url: RFC3986_ formatted broker address. If `None`
                 will be used keyword arguments.
            host: broker hostname or ip address
            port: broker port
            login: username string.
            password: password string.
            virtualhost: virtualhost parameter.
            client_properties: custom client capability.
            ssl: use SSL for connection. Should be used with addition kwargs.
            ssl_options: A dict of values for the SSL connection.
            timeout: connection timeout in seconds
            ssl_context: ssl.SSLContext instance
            logger: logger to use inside broker
            log_level: broker inner messages log level
            log_fmt: custom log formatting string
            apply_types: wrap brokers handlers to FastDepends decorator
            consumers: max messages to proccess at the same time
            dependencies: dependencies applied to all broker hadlers
            decode_message: custom RabbitMessage decoder
            parse_message: custom IncomingMessage to RabbitMessage parser

        .. _RFC3986: https://goo.gl/MzgYAs
        .. _official Python documentation: https://goo.gl/pty9xA
        """
    async def connect(
        self,
        *,
        url: Union[str, URL, None] = None,
        host: str = "localhost",
        port: int = 5672,
        login: str = "guest",
        password: str = "guest",
        virtualhost: str = "/",
        ssl: bool = False,
        ssl_options: Optional[aio_pika.abc.SSLOptions] = None,
        ssl_context: Optional[SSLContext] = None,
        timeout: aio_pika.abc.TimeoutType = None,
        client_properties: Optional[FieldTable] = None,
    ) -> aio_pika.RobustConnection:
        """Connect to RabbitMQ

        URL string might be contain ssl parameters e.g.
        `amqps://user:pass@host:port/vhost?ca_certs=ca.pem&certfile=crt.pem&keyfile=key.pem`

        Args:
            url: RFC3986_ formatted broker address. If `None`
                 will be used keyword arguments.
            host: broker hostname or ip address
            port: broker port
            login: username string.
            password: password string.
            virtualhost: virtualhost parameter.
            client_properties: custom client capability.
            ssl: use SSL for connection. Should be used with addition kwargs.
            ssl_options: A dict of values for the SSL connection.
            timeout: connection timeout in seconds
            ssl_context: ssl.SSLContext instance

        Returns:
            aio_pika.Connection object

        _RFC3986: https://goo.gl/MzgYAs
        _official Python documentation: https://goo.gl/pty9xA
        """
    async def publish(  # type: ignore[override]
        self,
        message: PikaSendableMessage = "",
        queue: Union[RabbitQueue, str] = "",
        exchange: Union[RabbitExchange, str, None] = None,
        *,
        # publish kwargs
        routing_key: str = "",
        mandatory: bool = True,
        immediate: bool = False,
        timeout: aio_pika.abc.TimeoutType = None,
        # callback kwargs
        callback: bool = False,
        callback_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
        # message kwargs
        headers: Optional[aio_pika.abc.HeadersType] = None,
        content_type: Optional[str] = None,
        content_encoding: Optional[str] = None,
        persist: bool = False,
        priority: Optional[int] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        expiration: Optional[aio_pika.abc.DateType] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[aio_pika.abc.DateType] = None,
        type: Optional[str] = None,
        user_id: Optional[str] = None,
        app_id: Optional[str] = None,
    ) -> Optional[Union[aiormq.abc.ConfirmationFrameType, DecodedMessage]]:
        """Publish the message to the exchange with the routing key.

        Args:
            message: encodable message to send
            queue: if routing key is not set, use queue instead
            exchange: exchange to publish message. Use `default` if not specified
            routing_key: message routing key
            mandatory: wait for message will be placed in any queue
            immediate: expects available consumer
            timeout: request to RabbitMQ timeout
            headers: message headers (for consumers)
            content_type: message content-type to decode
            content_encoding: message encoding
            persist: restore message on RabbitMQ reboot
            priority: message priority
            correlation_id: correlation id to match message with response
            reply_to: queue to send response
            message_id: message identifier
            timestamp: message sending time
            expiration: message lifetime (in seconds)
            type: message type (for consumers)
            user_id: RabbitMQ user who sent the message
            app_id: application identifier (for consumers)
            callback: wait for response
            callback_timeout: response waiting time
            raise_timeout: if False timeout returns None instead TimeoutError

        Returns:
            `aiormq.abc.ConfirmationFrameType` if you are not waiting for response
            (reply_to and callback are not specified)

            `DecodedMessage` | `None` if response is expected

        _publisher confirms: https://www.rabbitmq.com/confirms.html
        """
    def handle(  # type: ignore[override]
        self,
        queue: Union[str, RabbitQueue],
        exchange: Union[str, RabbitExchange, None] = None,
        *,
        consume_arguments: Optional[AnyDict] = None,
        retry: Union[bool, int] = False,
        dependencies: Sequence[Depends] = (),
        decode_message: AsyncDecoder[IncomingMessage] = None,
        parse_message: AsyncParser[IncomingMessage] = None,
        # AsyncAPI
        description: str = "",
    ) -> Callable[
        [HandlerCallable[T_HandlerReturn]],
        Callable[[IncomingMessage, bool], Awaitable[T_HandlerReturn]],
    ]:
        """Register queue consumer method

        Args:
            queue: queue to consume messages
            exchange: exchange to bind queue
            retry: at message exception will returns to queue `int` times or endless if `True`
            dependencies: wrap handler dependencies
            decode_message: custom RabbitMessage decoder
            parse_message: custom IncomingMessage to RabbitMessage parser
            description: AsyncAPI channel object description

        Returns:
            Async or sync function decorator
        """
    async def start(self) -> None:
        """Initialize RabbitMQ connection and startup all consumers"""
    async def close(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exec_tb: Optional[TracebackType] = None,
    ) -> None:
        """Close RabbitMQ connection"""
    async def declare_queue(self, queue: RabbitQueue) -> aio_pika.RobustQueue:
        """Check existence or create RabbitMQ queue"""
    async def declare_exchange(
        self, exchange: RabbitExchange
    ) -> aio_pika.RobustExchange:
        """Check existence or create RabbitMQ exchange"""
    @property
    def channel(self) -> aio_pika.RobustChannel:
        """Access to brokers' aio-pika channel object"""
    def _process_message(
        self,
        func: Callable[[RabbitMessage], Awaitable[T_HandlerReturn]],
        watcher: Optional[BaseWatcher],
    ) -> Callable[[RabbitMessage], Awaitable[T_HandlerReturn]]: ...
    def _get_log_context(  # type: ignore[override]
        self,
        message: Optional[RabbitMessage],
        queue: RabbitQueue,
        exchange: Optional[RabbitExchange] = None,
    ) -> Dict[str, Any]: ...
    async def _init_handler(
        self,
        handler: Handler,
    ) -> aio_pika.abc.AbstractRobustQueue: ...
    @classmethod
    def _validate_message(
        cls: Type["RabbitBroker"],
        message: PikaSendableMessage,
        callback_queue: Optional[aio_pika.abc.AbstractRobustQueue] = None,
        **message_kwargs: Dict[str, Any],
    ) -> aio_pika.Message: ...
    @staticmethod
    async def _parse_message(
        message: IncomingMessage,
    ) -> RabbitMessage: ...
    async def _connect(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> aio_pika.RobustConnection: ...
