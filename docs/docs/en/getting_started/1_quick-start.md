# QUICK START 

Install using `pip`:

=== "Redis"
    <div class="termy">
    ```console
    $ pip install "propan[async-redis]"
    ---> 100%
    ```
    </div>
    !!! tip
        To working with project start a test broker container
        ```bash
        docker run -d --rm -p 6379:6379 --name test-mq redis
        ```

=== "RabbitMQ"
    <div class="termy">
    ```console
    $ pip install "propan[async-rabbit]"
    ---> 100%
    ```
    </div>
    !!! tip
        To working with project start a test broker container
        ```bash
        docker run -d --rm -p 5672:5672 --name test-mq rabbitmq
        ```

=== "NATS"
    <div class="termy">
    ```console
    $ pip install "propan[async-nats]"
    ---> 100%
    ```
    </div>
    !!! tip
        To working with project start a test broker container
        ```bash
        docker run -d --rm -p 4222:4222 --name test-mq nats
        ```

## Basic usage

Create an application with the following code at `serve.py`:

=== "Redis"
    ```python linenums="1"
    {!> docs_src/index/01_redis_base.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1"
    {!> docs_src/index/01_rabbit_base.py!}
    ```

=== "NATS"
    ```python linenums="1"
    {!> docs_src/index/01_nats_base.py!}
    ```

And just run it:

<div class="termy">
```console
$ propan run serve:app

2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

---

## Type casting

Propan uses `pydantic` to cast incoming function arguments to types according to their annotation.

=== "Redis"
    ```python linenums="1" hl_lines="12"
    {!> docs_src/index/02_redis_type_casting.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="12"
    {!> docs_src/index/02_rabbit_type_casting.py!}
    ```

=== "NATS"
    ```python linenums="1" hl_lines="12"
    {!> docs_src/index/02_nats_type_casting.py!}
    ```

---

## Dependencies

**Propan** a has dependencies management policy close to `pytest fixtures`.
You can specify in functions arguments which dependencies
you would to use. Framework passes them from the global Context object.

Already existed context fields are: *app*, *broker*, *context* (itself), *logger* and *message*.
If you call not existing field, raises *pydantic.error_wrappers.ValidationError* value.

But you can specify your own dependencies, call dependencies functions (like `Fastapi Depends`)
and [more](../5_dependency/1_di-index).

=== "Redis"
    ```python linenums="1" hl_lines="11-12"
    {!> docs_src/index/03_redis_dependencies.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="11-12"
    {!> docs_src/index/03_rabbit_dependencies.py!}
    ```

=== "NATS"
    ```python linenums="1" hl_lines="11-12"
    {!> docs_src/index/03_nats_dependencies.py!}
    ```

---

## Project template

Also, **Propan CLI** is able to generate a production-ready application template:

<div class="termy">
```console
$ propan create [projectname]
Create Propan project template at: /home/user/projectname
```
</div>

!!! note
    Project template require `pydantic[dotenv]` installation to run

Just run the created project:

<div class="termy">
```console
### Run rabbimq first
$ docker compose --file [projectname]/docker-compose.yaml up -d

### Run project
$ propan run [projectname].app.serve:app --env=.env --reload

2023-04-10 23:39:41,140 INFO     - Started reloader process [115536] using WatchFiles
2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

Now you can enjoy a new development experience!

---

## HTTP Frameworks integrations

### Any Framework

You can use **Propan** `MQBrokers` without `PropanApp`.
Just *start* and *stop* them according to your application lifespan.

=== "Redis"
    ```python linenums="1" hl_lines="5 11-13 16-17"
    {!> docs_src/index/05_redis_http_example.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="5 11-13 16-17"
    {!> docs_src/index/05_rabbit_http_example.py!}
    ```

=== "NATS"
    ```python linenums="1" hl_lines="5 11-13 16-17"
    {!> docs_src/index/05_nats_http_example.py!}
    ```

### **FastAPI** Plugin

Also, **Propan** can be used as part of **FastAPI**.

Just import a **PropanRouter** you need and declare the message handler
using the `@event` decorator. This decorator is similar to the decorator `@handle` for the corresponding brokers.

!!! tip
    When used in this way, **Propan** does not use its own dependency system, but integrates into **FastAPI**.
    That is, you can use `Depends`, `Background Tasks` and other tools **Facet API** as if it were a regular HTTP endpoint.

=== "Redis"
    ```python linenums="1" hl_lines="7 15 19"
    {!> docs_src/index/06_redis_native_fastapi.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="7 15 19"
    {!> docs_src/index/06_rabbit_native_fastapi.py!}
    ```

!!! note
    More integration examples you can find [here](../../integrations/1_integrations-index/)

??? tip "Don't forget to stop test broker container"
    ```bash
    $ docker container stop test-mq
    ```