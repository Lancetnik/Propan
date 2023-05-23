import asyncio
from dataclasses import dataclass, field
from typing import Any, List, Optional

from aiokafka import AIOKafkaConsumer

from propan.brokers.model.schemas import BaseHandler
from propan.types import AnyDict


@dataclass
class Handler(BaseHandler):
    topics: List[str]

    consumer: Optional[AIOKafkaConsumer] = None
    task: Optional["asyncio.Task[Any]"] = None
    consumer_kwargs: AnyDict = field(default_factory=dict)
