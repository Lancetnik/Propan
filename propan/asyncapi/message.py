from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from propan.asyncapi.utils import AsyncAPIExternalDocs, AsyncAPITag


class AsyncAPICorrelationId(BaseModel):
    description: Optional[str] = None
    location: str


class AsyncAPIMessage(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    message_id: Optional[str] = Field(
        default=None,
        alias="messageId",
    )
    correlation_id: Optional[AsyncAPICorrelationId] = Field(
        default=None,
        alias="correlationId",
    )
    content_type: Optional[str] = Field(
        default=None,
        alias="contentType",
    )

    payload: Dict[str, Any]
    # TODO:
    # headers
    # schemaFormat
    # bindings
    # examples
    # traits

    tags: Optional[List[AsyncAPITag]] = None
    external_docs: Optional[AsyncAPIExternalDocs] = Field(
        default=None,
        alias="externalDocs",
    )
