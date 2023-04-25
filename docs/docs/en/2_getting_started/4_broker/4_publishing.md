# Message Publishing 

**Propan** has a unified method to send messages

```python
await broker.pubslih(message, ...)
```

This method, regardless of the broker, takes `message` as the first argument. However, the remaining arguments are
specific to different brokers.

You can get acquainted with all the features specific to your broker here:

* [RabbitBroker](../../../3_rabbit/5_publishing)
* [NatsBroker](../../../4_nats/3_publishing)

## Acceptable types to send

| Type | Header when sending | Method of conversion to bytes |
| -------------------- | --------------------------- | ---------------------------- |
| `dict`               | application/json            | json.dumps(message).encode() |
| `pydantic.BaseModel` | application/json            | message.json().encode()      |
| `str`                | text/plain                  | message.encode()             |
| `bytes`              |                             | message                      |

Also, some brokers support sending special types, which are described in the appropriate section of your broker's documentation.

## Initializing the broker before sending

To send a message to a queue, you must first connect to it.

If you are already inside a running **Propan** application, don't do anything: the broker is already running.
Just get access to it and send a message.

=== "RabbitMQ"
    ```python linenums="1" hl_lines="8"
    {!> docs_src/quickstart/broker/publishing/1_rabbit_inside_propan.py !}
    ```

=== "NATS"
    ```python linenums="1" hl_lines="8"
    {!> docs_src/quickstart/broker/publishing/1_nats_inside_propan.py !}
    ```

If you use **Propan** only to send asynchronous messages within another framework, you can use
the broker as a context manager for sending.

=== "RabbitMQ"
    ```python
    {!> docs_src/quickstart/broker/publishing/2_rabbit_context.py !}
    ```

=== "NATS"
    ```python
    {!> docs_src/quickstart/broker/publishing/2_nats_context.py !}
    ```

!!! tip
    Within this context, you can send an unlimited number of messages, as well as synchronously wait for a response to them.
    However, you cannot initialize the `handle` within this context: they will complete their execution with the context.

    This will be discussed in more detail in the next section.