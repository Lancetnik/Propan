from typing import Optional, Union

import aio_pika
from typing_extensions import TypeAlias

from propan.types import SendableMessage

TimeoutType: TypeAlias = Optional[Union[int, float]]
AioPikaSendableMessage: TypeAlias = Union[aio_pika.Message, SendableMessage]
