# Message Publishing

**Propan** uses a unified method to send messages

```python
await broker.publish(message, ...)
```

This method, regardless of the broker, takes `message` as the first argument. However, the rest of the arguments are
specific to different brokers.

You can get acquainted with all the features specific to your broker here:

* [Redis](../../../redis/2_publishing)
* [RabbitBroker](../../../rabbit/4_publishing)
* [NatsBroker](../../../nats/3_publishing)

## Valid types to submit

| Type                 | Send header           | Method of casting to bytes         |
| -------------------- | --------------------- | ---------------------------------- |
| `dict`               | application/json      | json.dumps(message).encode()       |
| `Sequence`           | application/json      | json.dumps(message).encode()       |
| `pydantic.BaseModel` | application/json      | message.json().encode()            |
| `str`                | text/plain            | message.encode()                   |
| `bytes`              |                       | message                            |

Also, some brokers support sending special types, which are described in the relevant section of your broker's documentation.

## Broker initialization

To send a message to a queue, you must first connect to it.

If you are inside a running **Propan** application, you don't need to do anything: the broker is already running.
Just access it and send a message.

{! includes/getting_started/broker/publishing/1_inside_propan.md !}

If you are only using **Propan** to send asynchronous messages within another framework, you can use
broker as context manager to send.

{! includes/getting_started/broker/publishing/2_context.md !}

!!! tips
    Within this context, you can send an unlimited number of messages, as well as synchronously wait for a response to them.
    However, `handle` cannot be initialized within this context: they will complete their execution along with the context.

    This will be discribed in more detail in the next section.
