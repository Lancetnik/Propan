from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from propan.asyncapi.schema.bindings import OperationBinding
from propan.asyncapi.schema.message import AsyncAPIMessage
from propan.asyncapi.schema.utils import AsyncAPIExternalDocs, AsyncAPITag


class Subscription(BaseModel):
    operation_id: Optional[str] = Field(
        default=None,
        alias="operationId",
    )

    summary: Optional[str] = None
    description: Optional[str] = None

    bindings: Optional[OperationBinding] = None

    message: AsyncAPIMessage

    security: Optional[Dict[str, List[str]]] = None

    # TODO
    # traits

    tags: Optional[List[AsyncAPITag]] = None
    external_docs: Optional[AsyncAPIExternalDocs] = Field(
        default=None,
        alias="externalDocs",
    )
