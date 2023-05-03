# **FastAPI** Plugin

**Propan** can be used as a part of **FastAPI**.

Just import a **PropanRouter** you need and declare the message handler
using the `@event` decorator. This decorator is similar to the decorator `@handle` for the related brokers.

!!! tip
    When used in this way, **Propan** does not use its own dependency system, but integrates into **FastAPI**.
    That is, you can use `Depends`, `BackgroundTasks` and other **FastAPI** tools as if it were a regular HTTP endpoint.

    Note that the code below uses `fastapi.Depends`, not `propan.Depends`.

```python linenums="1" hl_lines="1 3 7 15 19 23"
{!> docs_src/integrations/fastapi_plugin_rabbit.py!}
```

When processing a message from a broker, the entire message body is placed simultaneously in both the `body` and `path` request parameters: you can get access to them
in any way convenient for you. The message header is placed in `headers`.

Also, this router can be fully used as an `HttpRouter` (of which it is the inheritor). So you can
use it to declare any `get`, `post`, `put` and other HTTP methods. For example, this is done at  **19** line.

### Sending messages

Inside each router there is a broker. You can easily access it if you need to send a message to MQ.

```python linenums="1" hl_lines="6 10"
{!> docs_src/integrations/fastapi_plugin_rabbit_send.py!}
```

You can use the following `Depends` to access the broker if you want to use it at different parts of your program.

```python linenums="1" hl_lines="8 14-15"
{!> docs_src/integrations/fastapi_plugin_rabbit_depends.py!}
```