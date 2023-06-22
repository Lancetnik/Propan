from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from propan.asyncapi.utils import AsyncAPITag


class AsyncAPIServer(BaseModel):
    url: str
    protocol: str
    description: Optional[str] = None
    protocol_version: Optional[str] = Field(
        default=None,
        alias="protocolVersion",
    )
    tags: Optional[List[AsyncAPITag]] = None
    security: Optional[Dict[str, List[str]]] = None

    # TODO:
    # variables
    # bindings
