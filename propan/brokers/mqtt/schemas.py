from dataclasses import dataclass

from fast_depends.core import CallModel

from propan.brokers._model.schemas import BaseHandler
from propan.types import DecoratedCallable


@dataclass
class Handler(BaseHandler):
    topic: str

    def __init__(
        self,
        callback: DecoratedCallable,
        dependant: CallModel,
        topic: str = "",
        _description: str = "",
    ):
        self.callback = callback
        self.dependant = dependant
        self._description = _description
        self.topic = topic
