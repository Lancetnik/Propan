# NATS Publishing

To send messages, `NatsBroker` uses the unified `publish` method.

```python
import asyncio
from propan import NatsBroker

async def pub():
    async with NatsBroker() as broker:
        await broker.publish("Hi!", subject="test")

asyncio.run(pub())
```

## Basic arguments

The `publish` method accepts the following arguments:

* `message`: bytes | str | dict | Sequence[Any] | pydatic.BaseModel - message to send
* `subject`: str - *subject*, where the message will be sent.

## Message Parameters

* `headers`: dict[str, Any] | None = None - headers of the message being sent (used by consumers)

## RPC arguments

Also `publish` supports common arguments for creating [*RPC* queries](../../getting_started/4_broker/5_rpc/#_3):

* `reply_to`: str = "" - which *channel* to send the response to (used for asynchronous RPC requests)
* `callback`: bool = False - whether to expect a response to the message
* `callback_timeout`: float | None = 30.0 - timeout waiting for a response. In the case of `None` - waits indefinitely
* `raise_timeout`: bool = False
    * `False` - return None in case of timeout
    * `True` - error `asyncio.TimeoutError` in case of timeout
