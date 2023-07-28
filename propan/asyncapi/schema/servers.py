from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from propan.asyncapi.schema.bindings import ServerBinding
from propan.asyncapi.schema.utils import AsyncAPITag, Reference

SecurityRequirement = Dict[str, List[str]]


class AsyncAPIServerVariable(BaseModel):
    enum: Optional[List[str]] = None
    default: Optional[str] = None
    description: Optional[str] = None
    examples: Optional[List[str]] = None


class AsyncAPIServer(BaseModel):
    url: str
    protocol: str
    description: Optional[str] = None
    protocolVersion: Optional[str] = None
    tags: Optional[List[AsyncAPITag]] = None
    security: Optional[SecurityRequirement] = None
    variables: Optional[Dict[str, Union[AsyncAPIServerVariable, Reference]]] = None
    bindings: Optional[Union[ServerBinding, Reference]] = None
