from typing import List, Optional

from pydantic import BaseModel

from propan.asyncapi.schema.bindings import ChannelBinding, OperationBinding
from propan.asyncapi.schema.subscription import Subscription
from propan.asyncapi.schema.utils import Parameter


class Publish(BaseModel):
    bindings: Optional[OperationBinding] = None


class Channel(BaseModel):
    description: Optional[str] = None
    servers: Optional[List[str]] = None
    bindings: Optional[ChannelBinding] = None
    subscribe: Optional[Subscription] = None
    publish: Optional[Publish] = None
    parameters: Optional[Parameter] = None
