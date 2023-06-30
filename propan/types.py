from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, Sequence, Union

from pydantic import BaseModel
from typing_extensions import TypeAlias

AsyncFunc: TypeAlias = Callable[..., Awaitable[Any]]

AnyDict: TypeAlias = Dict[str, Any]
AnyCallable: TypeAlias = Callable[..., Any]
NoneCallable: TypeAlias = Callable[..., None]

DecoratedCallable: TypeAlias = AnyCallable
DecoratedCallableNone: TypeAlias = NoneCallable

JsonDecodable: TypeAlias = Union[
    float,
    int,
    bool,
    str,
    bytes,
]
DecodedMessage: TypeAlias = Union[
    Dict[str, JsonDecodable], Sequence[JsonDecodable], JsonDecodable
]
SendableMessage: TypeAlias = Union[
    datetime,
    DecodedMessage,
    BaseModel,
    None,
]
