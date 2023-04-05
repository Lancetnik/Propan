from dataclasses import dataclass
from typing import Callable, Optional, Sequence

from pydantic import BaseModel

from nats.js import api
from nats.aio.subscription import Subscription


@dataclass
class Handler:
    callback: Callable
    subject: str
    queue: str = ""

    subscription: Optional[Subscription] = None


class JetStream(BaseModel):
    prefix: str = api.DEFAULT_PREFIX
    domain: Optional[str] = None
    timeout: float = 5
    
    subjects: Sequence[str] = []
