from typing import List, Optional

from pydantic import BaseModel

from propan.asyncapi.bindings import AsyncAPIChannelBinding, AsyncAPIOperationBinding
from propan.asyncapi.subscription import AsyncAPISubscription


class AsyncAPIPublish(BaseModel):
    bindings: Optional[AsyncAPIOperationBinding] = None


class AsyncAPIChannelParameters(BaseModel):
    # TODO
    ...


class AsyncAPIChannel(BaseModel):
    description: Optional[str] = None
    servers: Optional[List[str]] = None
    bindings: Optional[AsyncAPIChannelBinding] = None
    subscribe: Optional[AsyncAPISubscription] = None
    publish: Optional[AsyncAPIPublish] = None
    parameters: Optional[AsyncAPIChannelParameters] = None
