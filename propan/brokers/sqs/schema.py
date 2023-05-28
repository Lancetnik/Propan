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


class FifoQueue(SQSQueue):
    fifo: bool = Field(True, alias="FifoQueue")
    content_based_deduplication: bool = Field(True, alias="ContentBasedDeduplication")


@dataclass
class Handler(BaseHandler):
    queue: SQSQueue
    consumer_params: Dict[str, Any]

    task: Optional["asyncio.Task[Any]"] = None
