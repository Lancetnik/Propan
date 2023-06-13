# **FastAPI** Plugin

## Handle messages

**Propan** can be used as a part of **FastAPI**.

Just import a **PropanRouter** you need and declare the message handler
using the `@event` decorator. This decorator is similar to the decorator `@handle` for the related brokers.

!!! tip
    When used in this way, **Propan** does not use its own dependency system, but integrates into **FastAPI**.
    That is, you can use `Depends`, `BackgroundTasks` and other **FastAPI** tools as if it were a regular HTTP endpoint.

    Note that the code below uses `fastapi.Depends`, not `propan.Depends`.

{! includes/integrations/fastapi/fastapi_plugin.md !}

When processing a message from a broker, the entire message body is placed simultaneously in both the `body` and `path` request parameters: you can get access to them
in any way convenient for you. The message header is placed in `headers`.

Also, this router can be fully used as an `HttpRouter` (of which it is the inheritor). So you can
use it to declare any `get`, `post`, `put` and other HTTP methods. For example, this is done at  **19** line.

## Sending messages

Inside each router there is a broker. You can easily access it if you need to send a message to MQ.

{! includes/integrations/fastapi/fastapi_plugin_send.md !}

You can use the following `Depends` to access the broker if you want to use it at different parts of your program.

{! includes/integrations/fastapi/fastapi_plugin_depends.md !}

Or you can access broker from a **FastAPI** application state

```python
{! docs_src/integrations/fastapi/request.py !}
```

## @after_startup

The `PropanApp` application has the `after_startup` hook, which allows you to perform operations with your message broker after the connection is established. This can be extremely convenient for managing your brokers' objects and/or sending messages. This hook is also available for your **FastAPI PropanRouter**

{! includes/integrations/fastapi/after_startup.md !}

## Documentation

When using **Propan** as a router for **FastAPI**, the framework automatically registers endpoints for hosting **AsyncAPI** documentation into your application with the following default values:

```python linenums='1'
{!> docs_src/quickstart/documentation/fastapi.py !}
```
