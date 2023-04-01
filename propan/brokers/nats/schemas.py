from dataclasses import dataclass
from typing import Callable, Optional

from nats.aio.subscription import Subscription


@dataclass
class Handler:
    callback: Callable
    subject: str
    queue: str = ""

    subscription: Optional[Subscription] = None
