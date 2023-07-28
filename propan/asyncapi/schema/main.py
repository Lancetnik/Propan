from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from propan.asyncapi.schema.channels import AsyncAPIChannel
from propan.asyncapi.schema.info import AsyncAPIInfo
from propan.asyncapi.schema.message import AsyncAPIMessage
from propan.asyncapi.schema.servers import AsyncAPIServer
from propan.asyncapi.schema.utils import AsyncAPIExternalDocs, AsyncAPITag
from propan.constants import ContentTypes
from propan.types import AnyDict

ASYNC_API_VERSION = "2.6.0"


class AsyncAPIComponents(BaseModel):
    # TODO
    # servers
    # serverVariables
    # channels
    messages: Optional[Dict[str, AsyncAPIMessage]] = None
    schemas: Optional[Dict[str, AnyDict]] = None

    # securitySchemes
    # parameters
    # correlationIds
    # operationTraits
    # messageTraits
    # serverBindings
    # channelBindings
    # operationBindings
    # messageBindings


class AsyncAPISchema(BaseModel):
    asyncapi: str = ASYNC_API_VERSION
    id: Optional[str] = None
    default_content_type: str = Field(
        default=ContentTypes.json.value,
        alias="defaultContentType",
    )
    info: AsyncAPIInfo
    servers: Optional[Dict[str, AsyncAPIServer]] = None
    channels: Dict[str, AsyncAPIChannel]
    components: Optional[AsyncAPIComponents] = None
    tags: Optional[List[AsyncAPITag]] = None
    external_docs: Optional[AsyncAPIExternalDocs] = Field(
        default=None,
        alias="externalDocs",
    )
