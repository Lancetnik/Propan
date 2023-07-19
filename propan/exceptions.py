class SkipMessage(Exception):
    """PushBackWatcher Instruction to skip message"""


class HandlerException(Exception):
    """Base Handler Exception"""


class StopConsume(HandlerException):
    """Raise it to stop Handler consuming"""


class RuntimeException(Exception):
    """Base Processing level Exception"""


class AckMessage(HandlerException):
    """Raise it to stop `ack` a message immediately"""


class NackMessage(HandlerException):
    """Raise it to stop `nack` a message immediately"""


class RejectMessage(HandlerException):
    """Raise it to stop `reject` a message immediately"""


WRONG_PUBLISH_ARGS = ValueError(
    "You should use `reply_to` to send response to long-living queue "
    "and `rpc` to get response in sync mode."
)
