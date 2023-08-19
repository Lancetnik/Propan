from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from propan.asyncapi.schema.bindings import ServerBinding
from propan.asyncapi.schema.utils import Reference, Tag, TagDict

SecurityRequirement = Dict[str, List[str]]


class ServerVariable(BaseModel):
    enum: Optional[List[str]] = None
    default: Optional[str] = None
    description: Optional[str] = None
    examples: Optional[List[str]] = None


class Server(BaseModel):
    url: str
    protocol: str
    description: Optional[str] = None
    protocolVersion: Optional[str] = None
    tags: Optional[List[Union[Tag, TagDict, Dict[str, Any]]]] = None
    security: Optional[SecurityRequirement] = None
    variables: Optional[Dict[str, Union[ServerVariable, Reference]]] = None
    bindings: Optional[Union[ServerBinding, Reference]] = None
