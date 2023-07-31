from typing import Any, Dict, Optional

from pydantic import BaseModel
from typing_extensions import Literal


class ServerBinding(BaseModel):
    bindingVersion: str = "custom"


class ChannelBinding(BaseModel):
    channel: str
    method: Literal["ssubscribe", "psubscribe", "subscribe"] = "subscribe"
    bindingVersion: str = "custom"


class OperationBinding(BaseModel):
    replyTo: Optional[Dict[str, Any]] = None
    bindingVersion: str = "custom"
