import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from redis.asyncio.client import PubSub

from propan.brokers.model.schemas import BaseHandler


@dataclass
class Handler(BaseHandler):
    channel: str
    pattern: bool = False

    task: Optional["asyncio.Task[Any]"] = None
    subscription: Optional[PubSub] = None


class RedisMessage(BaseModel):
    data: bytes
    headers: Dict[str, str] = Field(default_factory=dict)
    reply_to: str = ""
