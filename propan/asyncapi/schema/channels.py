from typing import List, Optional

from pydantic import BaseModel

from propan.asyncapi.schema.bindings import ChannelBinding
from propan.asyncapi.schema.operations import Operation
from propan.asyncapi.schema.utils import Parameter


class Channel(BaseModel):
    description: Optional[str] = None
    servers: Optional[List[str]] = None
    bindings: Optional[ChannelBinding] = None
    subscribe: Optional[Operation] = None
    publish: Optional[Operation] = None
    parameters: Optional[Parameter] = None
