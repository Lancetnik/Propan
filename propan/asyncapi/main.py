from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from propan.asyncapi.channels import AsyncAPIChannel
from propan.asyncapi.info import AsyncAPIInfo
from propan.asyncapi.message import AsyncAPIMessage
from propan.asyncapi.servers import AsyncAPIServer
from propan.asyncapi.utils import AsyncAPIExternalDocs, AsyncAPITag
from propan.brokers.constants import ContentTypes
from propan.types import AnyDict

ASYNC_API_VERSION = "2.6.0"


class AsyncAPIComponents(BaseModel):
    # TODO
    # servers
    # serverVariavles
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
    default_content_type: str = Field(
        default=ContentTypes.json.value,
        alias="defaultContentType",
    )
    info: AsyncAPIInfo
    servers: Optional[Dict[str, AsyncAPIServer]] = None
    channels: Dict[str, AsyncAPIChannel]
    tags: Optional[List[AsyncAPITag]] = None
    external_docs: Optional[AsyncAPIExternalDocs] = Field(
        default=None,
        alias="externalDocs",
    )

    # TODO:
    # id
    components: Optional[AsyncAPIComponents] = None
