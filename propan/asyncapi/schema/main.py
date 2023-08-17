from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from propan._compat import model_to_json, model_to_jsonable
from propan.asyncapi.schema.channels import Channel
from propan.asyncapi.schema.info import Info
from propan.asyncapi.schema.message import Message
from propan.asyncapi.schema.servers import Server
from propan.asyncapi.schema.utils import ExternalDocs, Tag

ASYNC_API_VERSION = "2.6.0"


class Components(BaseModel):
    # TODO
    # servers
    # serverVariables
    # channels
    messages: Optional[Dict[str, Message]] = None
    schemas: Optional[Dict[str, Dict[str, Any]]] = None

    # securitySchemes
    # parameters
    # correlationIds
    # operationTraits
    # messageTraits
    # serverBindings
    # channelBindings
    # operationBindings
    # messageBindings


class Schema(BaseModel):
    asyncapi: str = ASYNC_API_VERSION
    id: Optional[str] = None
    defaultContentType: Optional[str] = None
    info: Info
    servers: Optional[Dict[str, Server]] = None
    channels: Dict[str, Channel]
    components: Optional[Components] = None
    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocs] = None

    def to_jsonable(self) -> Any:
        return model_to_jsonable(
            self,
            by_alias=True,
            exclude_none=True,
        )

    def to_json(self) -> str:
        return model_to_json(
            self,
            by_alias=True,
            exclude_none=True,
        )
