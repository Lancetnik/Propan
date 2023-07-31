from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ServerBinding(BaseModel):
    bindingVersion: str = "0.4.0"


class ChannelBinding(BaseModel):
    topic: List[str]
    partitions: Optional[int] = None
    replicas: Optional[int] = None
    # TODO:
    # topicConfiguration
    bindingVersion: str = "0.4.0"


class OperationBinding(BaseModel):
    groupId: Optional[Dict[str, Any]] = None
    clientId: Optional[Dict[str, Any]] = None
    replyTo: Optional[Dict[str, Any]] = None
    bindingVersion: str = "0.4.0"
