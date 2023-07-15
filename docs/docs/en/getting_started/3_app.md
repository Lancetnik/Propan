# **PropanApp**

If you are using the **Propan CLI**, you need to create an instance of the application for the project to work:

```python
from propan import PropanApp
app = PropanApp()
```

!!! tip
    When initializing, `PropanApp` writes itself to `ContextRepo` with the name `"app"`, so you can always access it from [context](../5_dependency/2_context).

## Using Brokers

In order for `PropanApp` to launch your broker, you need to put it in the application object.

This is usually done when declaring the application itself:

{! includes/getting_started/app/1_broker.md !}

But, sometimes you may need to initialize the broker elsewhere. In this case, you can use the `app.set_broker` method:

{! includes/getting_started/app/2_set_broker.md !}

## Launching other apps

If the broker is not passed to `PropanApp`, the following functions will still work:

* Life Cycle Hooks
* Hot-reload code
* Multiprocessing of execution

In fact, as a broker, you can pass an instance of any class that will have asynchronous methods `start` and `close`:

```python
class ABCBroker:
    async def start(self) -> None:
        ...
    
    async def close(self) -> None:
        ...
```

If your code satisfies this interface, **PropanApp** can be used as a convenient tool for project management.