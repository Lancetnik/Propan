# Routing

## General behavior

To declare a broker message handler function, use the decorator `@broker.handle`

```python
@broker.handle("test")
async def base_handler(body: str):
    ...
```

This behavior is similar for all brokers, however, the parameters passed to `@broker.handle` are specific for each broker.

To learn more about the behavior of specialized brokers, go to the following sections:

* [RabbitBroker](../../../3_rabbit/1_routing)
* [NatsBroker](../../../4_nats/2_routing)

## Error handling

However, all brokers have the `retry` flag in the `@broker.hanle` method, which is responsible for error handling logic.

By default, this flag has the value `False`, which indicates that if an error occurred during message processing, it will still be retrieved from the queue.

```python
@broker.handle("test", retry=False) # don't handle exceptions
async def base_handler(body: str):
    ...
```

If this flag is set to `True`, the message will be placed back in the queue indefinitely when an error occurs. In this case, the message can be processed both by another consumer (if there are several of them) and by the same one.

```python
@broker.handle("test", retry=True)  # try again indefinitely
async def base_handler(body: str):
    ...
```

When setting the value `int` as the flag, the number of retries will be limited to this number.

```python
@broker.handle("test", retry=3)     # make up to 3 attempts
async def base_handler(body: str):
    ...
```

!!! bug
    At the moment, attempts are taken into account only by the current consumer. If the message goes to another consumer, he will have his own counter.
    Subsequently, this logic will be reworked.

!!! tip
    At more complex error handling cases you can use [tenacity](https://tenacity.readthedocs.io/en/latest/){.external-link target="_blank"}