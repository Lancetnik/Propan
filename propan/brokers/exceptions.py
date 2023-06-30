class SkipMessage(Exception):
    """PushBackWatcher Instruction to skip message"""


WRONG_PUBLISH_ARGS = ValueError(
    "You should use `reply_to` to send response to long-living queue "
    "and `callback` to get response in sync mode."
)
