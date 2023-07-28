from typing import List, Optional

from pydantic import BaseModel

from propan.asyncapi.schema.bindings import ChannelBinding, OperationBinding
from propan.asyncapi.schema.subscription import Subscription
from propan.asyncapi.schema.utils import Parameter


class AsyncAPIPublish(BaseModel):
    bindings: Optional[OperationBinding] = None


class AsyncAPIChannel(BaseModel):
    description: Optional[str] = None
    servers: Optional[List[str]] = None
    bindings: Optional[ChannelBinding] = None
    subscribe: Optional[Subscription] = None
    publish: Optional[AsyncAPIPublish] = None
    parameters: Optional[Parameter] = None
