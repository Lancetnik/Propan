from dataclasses import dataclass
from typing import Optional, Sequence

from nats.aio.subscription import Subscription
from nats.js.api import DEFAULT_PREFIX
from propan.types import DecoratedCallable
from pydantic import BaseModel


@dataclass
class Handler:
    callback: DecoratedCallable
    subject: str
    queue: str = ""

    subscription: Optional[Subscription] = None


class JetStream(BaseModel):
    prefix: str = DEFAULT_PREFIX
    domain: Optional[str] = None
    timeout: float = 5

    subjects: Sequence[str] = []
