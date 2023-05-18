# RPC

## Reasons to use RPC over MQ

Sometimes you may need to not just send a message but also get a response to it.
HTTP is usually used for this, but we already have a message delivery system, so why don't we use it?

**RPC** requests on top of message brokers are executed very simply: we send a message to one queue, and receive a response from another.
It looks a bit awkward, but this strategy has some advantages.

1. **The time** between a request and a response is unlimited: we can send a request, and receive a response in a day. The HTTP request does not allow us such do that.
    This can be extremely useful for services that perform long-term work: process files, run neural networks, etc.
2. **Asynchrony**: we can decide for ourselves whether to wait for an answer right now or just send a request and process it when it is ready.
3. **One request - many responses**: Using message brokers, we may get many responses to a single request. For example, with a request, we can initialize a communication channel through which data will be sent back as soon as it is ready.

## Implementation

### Server

From the server side (the receiving side), you do not need to change the code: `return` of your function will be automatically sent to the client if he is waiting for a response to your message.

!!! note
    The result of your function must match the valid types of the `message` parameter of the `broker.publish` function.

    Acceptable types are `str`, `dict`, `Sequence`, `pydantic.BaseModel`, `bytes` and a native message of the library used for the broker.

=== "Redis"
    ```python linenums="1" hl_lines="7"
    {!> docs_src/quickstart/broker/rpc/1_redis_handler.py !}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="7"
    {!> docs_src/quickstart/broker/rpc/1_rabbit_handler.py !}
    ```

### Client

#### Blocking request

To wait for the result of executing the request "right here" (as if it were an HTTP request), you just need to specify the parameter `callback=True` when sending the message.

=== "Redis"
    ```python linenums="1" hl_lines="8"
    {!> docs_src/quickstart/broker/rpc/2_redis_blocking_client.py !}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="8"
    {!> docs_src/quickstart/broker/rpc/2_rabbit_blocking_client.py !}
    ```

To set the time that the client is ready to wait for a response from the server, use the`callback_timeout` parameter (by default - **30** seconds)

=== "Redis"
    ```python linenums="1" hl_lines="5"
    {!> docs_src/quickstart/broker/rpc/3_redis_blocking_client_timeout.py !}
    ```

    1. Waits for the result for 3 seconds

=== "RabbitMQ"
    ```python linenums="1" hl_lines="5"
    {!> docs_src/quickstart/broker/rpc/3_rabbit_blocking_client_timeout.py !}
    ```

    1. Waits for the result for 3 seconds

If you are ready to wait for a response as long as it takes, you can set `callback_timeout=None`

=== "Redis"
    ```python linenums="1" hl_lines="5"
    {!> docs_src/quickstart/broker/rpc/4_redis_blocking_client_timeout_none.py !}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="5"
    {!> docs_src/quickstart/broker/rpc/4_rabbit_blocking_client_timeout_none.py !}
    ```

!!! warning
    This code will wait for a response indefinitely, even if the server is unable to process the message or processing takes a long time.

By default, if **Propan** did not wait for the server response, the function will return `None`. If you want to explicitly process `asyncio.TimeoutError`, use the `raise_timeout` parameter.

=== "Redis"
    ```python linenums="1" hl_lines="5"
    {!> docs_src/quickstart/broker/rpc/5_redis_blocking_client_timeout_error.py !}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="5"
    {!> docs_src/quickstart/broker/rpc/5_rabbit_blocking_client_timeout_error.py !}
    ```

#### Non-blocking request

To process the response outside of the main execution loop, you can initialize a handler and then pass its queue as the `reply_to` argument of the request.

=== "Redis"
    ```python linenums="1" hl_lines="6 16"
    {!> docs_src/quickstart/broker/rpc/6_noblocking_client_redis.py !}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="6 16"
    {!> docs_src/quickstart/broker/rpc/6_noblocking_client_rabbit.py !}
    ```

!!! note
    Note that the `broker` must be running to consume non-blocking messages. This means we cannot work with non-blocking RPC messages using `broker` as a context manager.
