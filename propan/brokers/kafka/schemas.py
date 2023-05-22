import asyncio
from dataclasses import dataclass
from typing import Any, List, Optional

from aiokafka import AIOKafkaConsumer

from propan.brokers.model.schemas import BaseHandler


@dataclass
class Handler(BaseHandler):
    topics: List[str]

    consumer: Optional[AIOKafkaConsumer] = None
    task: Optional["asyncio.Task[Any]"] = None
