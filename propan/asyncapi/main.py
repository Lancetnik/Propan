from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from propan.asyncapi.channels import AsyncAPIChannel
from propan.asyncapi.info import AsyncAPIInfo
from propan.asyncapi.servers import AsyncAPIServer
from propan.asyncapi.utils import AsyncAPIExternalDocs, AsyncAPITag
from propan.brokers._model.schemas import ContentTypes

ASYNC_API_VERSION = "2.6.0"


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
    # components

    class Config:
        allow_population_by_field_name = True
