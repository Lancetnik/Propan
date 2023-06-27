# Redis Publishing

To send messages, `RedisBroker` also uses the unified `publish` method.

```python
import asyncio
from propan import RedisBroker

async def pub():
    async with RedisBroker() as broker:
        await broker.publish("Hi!", channel="test")

asyncio.run(pub())
```

## Basic arguments

The `publish` method accepts the following arguments:

* `message`: bytes | str | dict | Sequence[Any] | pydatic.BaseModel - message to send
* `channel`: str = "" - *channel* to which the message will be sent.

## Message Parameters

*Redis* by default sends a message in the form of raw `bytes'. So **Propan** uses its own message transmission format:
when calling the `publish` method, *json* is sent to *Redis* with the following fields:

```json
{
    "data": "",
    "headers": {},
    "reply_to": ""
}
```

Independently, you can set and use the headers of the sent message within your application (the `content-type` is automatically set there, according to which **Propan** determines how to decode the received message)

* `headers`: dict[str, Any] | None = None - headers of the message being sent (used by consumers)

!!! note ""
    If **Propan** receives a message sent using another library or framework (or just a message in a different format),
    the entire body of this message will be perceived as the `data` field of the received message, and the `content-type` will be recognized automatically.

    At the same time, **RPC** requests will not work, since there is no `reply_to` field in the incoming message.

## RPC arguments

Also `publish` supports common arguments for making [*RPC* requests](../../getting_started/4_broker/5_rpc/#client):

* `reply_to`: str = "" - which *channel* to send the response to (used for asynchronous RPC requests)
* `callback`: bool = False - whether to expect a response to the message
* `callback_timeout`: float | None = 30.0 - timeout waiting for a response. In the case of `None` - waits indefinitely
* `raise_timeout`: bool = False
    * `False` - return None in case of timeout
    * `True` - error `TimeoutError` in case of timeout
