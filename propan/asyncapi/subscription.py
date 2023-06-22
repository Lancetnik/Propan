from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from propan.asyncapi.bindings import AsyncAPIOperationBinding
from propan.asyncapi.message import AsyncAPIMessage
from propan.asyncapi.utils import AsyncAPIExternalDocs, AsyncAPITag


class AsyncAPISubscription(BaseModel):
    operation_id: Optional[str] = Field(
        default=None,
        alias="operationId",
    )

    summary: Optional[str] = None
    description: Optional[str] = None

    bindings: Optional[AsyncAPIOperationBinding] = None

    message: AsyncAPIMessage

    security: Optional[Dict[str, List[str]]] = None

    # TODO
    # traits

    tags: Optional[List[AsyncAPITag]] = None
    external_docs: Optional[AsyncAPIExternalDocs] = Field(
        default=None,
        alias="externalDocs",
    )
