from typing import Dict, List, Optional

from pydantic import BaseModel

from propan.asyncapi.schema.bindings import OperationBinding
from propan.asyncapi.schema.message import Message
from propan.asyncapi.schema.utils import ExternalDocs, Tag


class Operation(BaseModel):
    operationId: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None

    bindings: Optional[OperationBinding] = None

    message: Message

    security: Optional[Dict[str, List[str]]] = None

    # TODO
    # traits

    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocs] = None
