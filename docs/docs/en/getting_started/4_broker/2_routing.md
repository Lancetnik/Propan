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

* [RabbitBroker](../../../rabbit/1_routing/#routing-rules)
* [NatsBroker](../../../nats/1_nats-index/#routing-rules)
* [RedisBroker](../../../redis/1_redis-index/#routing-rules)

## BrokerRouter

Sometimes it can be convenient to divide handlers into groups that can be connected to your application with just one command.
To do this, **Propan** provides **BrokerRouter**: you can register your handlers within the router, and then connect this router to your broker.

This will help to better organize your application's code and also allow you to divide it into plug-ins.

{! includes/getting_started/broker/routers.md !}

In this case, the router prefix will be added to the name of the queue of your handlers.

```python hl_lines="3"
{!> docs_src/quickstart/broker/routers/publish.py !}
```

## Error handling

However, all brokers supporting acknowledgement have the `retry` flag in the `@broker.hanle` method, which is responsible for error handling logic.

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