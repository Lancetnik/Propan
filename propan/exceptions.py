class SkipMessage(Exception):
    """PushBackWatcher Instruction to skip message"""


class HandlerException(Exception):
    """Base Handler Exception"""


class StopConsume(HandlerException):
    """Raise it to stop Handler consuming"""


WRONG_PUBLISH_ARGS = ValueError(
    "You should use `reply_to` to send response to long-living queue "
    "and `rpc` to get response in sync mode."
)
