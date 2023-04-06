from contextvars import ContextVar
from typing import Any, Dict

from propan.utils.classes import Singlethon

message = ContextVar("message", default=None)
log_context = ContextVar("message", default={})


class Context(Singlethon):
    _context: Dict[str, Any] = {}

    def set_context(self, key: str, v: Any):
        self._context[key] = v

    def remove_context(self, key: str):
        self._context.pop(key, None)

    def clear(self):
        self._context = {}

    def __getattr__(self, __name: str) -> Any:
        return self.context.get(__name)

    @property
    def context(self):
        return {**self._context, "context": self, "message": message.get()}


context = Context()
