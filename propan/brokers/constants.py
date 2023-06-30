from enum import Enum

from typing_extensions import TypeAlias

ContentType: TypeAlias = str


class ContentTypes(str, Enum):
    text = "text/plain"
    json = "application/json"
