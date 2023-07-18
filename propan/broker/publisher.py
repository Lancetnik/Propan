from dataclasses import dataclass
from typing import Optional

from propan.broker.types import HandlerCallable


@dataclass
class BasePublisher:
    call: Optional[HandlerCallable] = None
