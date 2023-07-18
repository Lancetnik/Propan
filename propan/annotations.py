import logging

from typing_extensions import Annotated, TypeVar

from propan.utils.context import Context as ContextField
from propan.utils.context import ContextRepo as CR
from propan.utils.no_cast import NoCast as NC

Logger = Annotated[logging.Logger, ContextField("logger")]
ContextRepo = Annotated[CR, ContextField("context")]
NoCast = Annotated[TypeVar("_NoCastType"), NC()]
