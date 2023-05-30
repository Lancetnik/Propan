import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

from pydantic import Field

from propan.brokers._model.schemas import BaseHandler, Queue


class SQSQueue(Queue):
    fifo: bool = Field(False, alias="FifoQueue")

    # policy: str = Field(..., alias="Policy")

    delay_seconds: int = Field(0, alias="DelaySeconds")  # 0...900
    max_message_size: int = Field(262_144, alias="MaximumMessageSize")  # 1024...262_144
    retention_period_sec: int = Field(
        345_600, alias="MessageRetentionPeriod"
    )  # 60...1_209_600
    receive_wait_time_sec: int = Field(
        0, alias="ReceiveMessageWaitTimeSeconds"
    )  # 0...20
    visibility_timeout_sec: int = Field(30, alias="VisibilityTimeout")  # 0...43_200

    def __init__(
        self,
        name: str,
        fifo: bool = False,
        delay_seconds: int = 0,
        max_message_size: int = 262_144,
        retention_period_sec: int = 345_600,
        receive_wait_time_sec: int = 0,
        visibility_timeout_sec: int = 30,
        **kwargs: Any,
    ):
        super().__init__(
            name=name,
            fifo=fifo,
            visibility_timeout_sec=visibility_timeout_sec,
            receive_wait_time_sec=receive_wait_time_sec,
            retention_period_sec=retention_period_sec,
            max_message_size=max_message_size,
            delay_seconds=delay_seconds,
            **kwargs,
        )


class FifoQueue(SQSQueue):
    fifo: bool = Field(default=True, alias="FifoQueue")
    content_based_deduplication: bool = Field(
        default=True, alias="ContentBasedDeduplication"
    )

    def __init__(
        self,
        name: str,
        fifo: bool = True,
        delay_seconds: int = 0,
        max_message_size: int = 262_144,
        retention_period_sec: int = 345_600,
        receive_wait_time_sec: int = 0,
        visibility_timeout_sec: int = 30,
        content_based_deduplication: bool = True,
    ):
        super().__init__(
            name=name,
            fifo=fifo,
            visibility_timeout_sec=visibility_timeout_sec,
            receive_wait_time_sec=receive_wait_time_sec,
            retention_period_sec=retention_period_sec,
            max_message_size=max_message_size,
            delay_seconds=delay_seconds,
            content_based_deduplication=content_based_deduplication,
        )


@dataclass
class Handler(BaseHandler):
    queue: SQSQueue
    consumer_params: Dict[str, Any]

    task: Optional["asyncio.Task[Any]"] = None
