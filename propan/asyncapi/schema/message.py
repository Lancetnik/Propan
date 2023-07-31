from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from propan.asyncapi.schema.utils import ExternalDocs, Tag


class CorrelationId(BaseModel):
    description: Optional[str] = None
    location: str


class Message(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    messageId: Optional[str] = None
    correlationId: Optional[CorrelationId] = None
    contentType: Optional[str] = None

    payload: Dict[str, Any]
    # TODO:
    # headers
    # schemaFormat
    # bindings
    # examples
    # traits

    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocs] = None
