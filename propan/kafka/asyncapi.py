from propan.kafka.handler import LogicHandler
from propan.kafka.publisher import LogicPublisher


class Handler(LogicHandler):
    pass


class Publisher(LogicPublisher):
    @property
    def name(self) -> str:
        return self.title or "undefined"
