from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Sequence, Union

from pydantic import BaseModel
from typing_extensions import ParamSpec, TypeAlias, TypeVar

AnyDict: TypeAlias = Dict[str, Any]

F_Return = TypeVar("F_Return")
F_Spec = ParamSpec("F_Spec")

AnyCallable: TypeAlias = Callable[..., Any]
NoneCallable: TypeAlias = Callable[..., None]
AsyncFunc: TypeAlias = Callable[..., Awaitable[Any]]

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

SendableReturn = TypeVar("SendableReturn", bound=SendableMessage)

SettingField: TypeAlias = Union[bool, str, List[str]]
