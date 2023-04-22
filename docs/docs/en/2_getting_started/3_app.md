# **PropanApp**

If you are using the **Propan CLI**, you need to create an instance of the application for the project to work

```python
from propan import PropanApp
app = PropanApp()
```

!!! tip
    At initializing, `PropanApp` writes itself to `ContextRepo` with the name `"app"`, so you can always access it from [context](../5_dependency/2_context).

## Using Brokers

In order for `PropanApp` to launch your broker, you need to put it in the application object.

This is usually done when declaring the application itself

=== "RabbitMQ"
    ```python
    {!> docs_src/quickstart/app/1_broker_rabbit.py!}
    ```

=== "NATS"
    ```python
    {!> docs_src/quickstart/app/1_broker_nats.py!}
    ```

But, sometimes you may need to initialize the broker elsewhere. In this case, you can use the `app.set_broker` method

=== "RabbitMQ"
    ```python
    {!> docs_src/quickstart/app/2_set_broker_rabbit.py!}
    ```

=== "NATS"
    ```python
    {!> docs_src/quickstart/app/2_set_broker_nats.py!}
    ```

## Launching other apps

If the broker is not passed to `PropanApp`, the following functions will still work:

* Life Cycle Hooks
* Hotreload code
* Multiprocessing of execution

In fact, as a broker, you can pass an instance of any class that will have asynchronous methods `start` and `close`

```python
class ABCBroker:
    async def start(self) -> None:
        ...
    
    async def close(self) -> None:
        ...
```

If your code satisfies this interface, **PropanApp** can be used as a convenient tool for project management.