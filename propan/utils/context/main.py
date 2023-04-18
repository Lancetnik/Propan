from contextvars import ContextVar
from typing import Any, Dict, Optional

from propan.utils.classes import Singlethon

message: ContextVar[Optional[str]] = ContextVar("message", default=None)
log_context: ContextVar[Dict[str, Any]] = ContextVar("message", default={})


class ContextRepo(Singlethon):
    _context: Dict[str, Any] = {}

    def set_context(self, key: str, v: Any) -> None:
        self._context[key] = v

    def remove_context(self, key: str) -> None:
        self._context.pop(key, None)

    def clear(self) -> None:
        self._context = {}

    def __getattr__(self, __name: str) -> Any:
        return self.context.get(__name)

    @property
    def context(self) -> Dict[str, Any]:
        return {**self._context, "context": self, "message": message.get()}


context: ContextRepo = ContextRepo()
