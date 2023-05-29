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
        To work with the project start a contianer with the test broker
        ```bash
        docker run -d --rm -p 5672:5672 --name test-mq rabbitmq
        ```

=== "Kafka"
    <div class="termy">
    ```console
    $ pip install "propan[async-kafka]"
    ---> 100%
    ```
    </div>
    !!! tip
        To work with the project start a container with the test broker
        ```bash
        docker run -d --rm -p 9092:9092 --name test-mq \
        -e KAFKA_ENABLE_KRAFT=yes \
        -e KAFKA_CFG_NODE_ID=1 \
        -e KAFKA_CFG_PROCESS_ROLES=broker,controller \
        -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
        -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
        -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
        -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://127.0.0.1:9092 \
        -e KAFKA_BROKER_ID=1 \
        -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:9093 \
        -e ALLOW_PLAINTEXT_LISTENER=yes \
        bitnami/kafka
        ```

=== "SQS"
    <div class="termy">
    ```console
    $ pip install "propan[async-sqs]"
    ---> 100%
    ```
    </div>
    !!! tip
        To work with the project start a container with the test broker
        ```bash
        docker run -d --rm -p 9324:9324 --name test-mq softwaremill/elasticmq-native
        ```

=== "NATS"
    <div class="termy">
    ```console
    $ pip install "propan[async-nats]"
    ---> 100%
    ```
    </div>
    !!! tip
        To work with the project start a container with the test broker
        ```bash
        docker run -d --rm -p 4222:4222 --name test-mq nats
        ```

## Basic usage

Create an application with the following code at `serve.py`:

{! includes/index/01_base.md !}

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

```python linenums="1" hl_lines="5 9"
{!> docs_src/index/02_type_casting.py!}
```

---

## Dependencies

**Propan** has a dependencies management policy close to `pytest fixtures`.
Function arguments declare which dependencies you want are needed, and a special decorator delivers them from the global Context object.

Already declared context fields are: *app*, *broker*, *context* (itself), *logger* and *message*.
If you call a non-existent field, raises *pydantic.error_wrappers.ValidationError* value.

But you can specify your own dependencies, call dependencies functions (like `Fastapi Depends`)
and [more](../5_dependency/1_di-index).

```python linenums="1" hl_lines="11-12"
{!> docs_src/index/03_dependencies.py!}
```

---

## Project template

Also, **Propan CLI** is able to generate a production-ready application template:

<div class="termy">
```console
$ propan create async [broker] [projectname]
Create Propan project template at: /home/user/projectname
```
</div>

!!! note
    Project template requires `pydantic[dotenv]` installation to run

Just run the created project:

<div class="termy">
```console
### Run broker first
$ docker compose --file [projectname]/docker-compose.yaml up -d [broker]

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

{! includes/index/04_http_example.md !}

### **FastAPI** Plugin

Also, **Propan** can be used as part of **FastAPI**.

Just import a **PropanRouter** you need and declare the message handler
using the `@event` decorator. This decorator is similar to the decorator `@handle` for the corresponding brokers.

!!! tip
    When used this way, **Propan** does not utilize its own dependency system, but integrates into **FastAPI**.
    That is, you can use `Depends`, `Background Tasks` and other tools **Facet API** as if it were a regular HTTP endpoint.

{! includes/index/05_native_fastapi.md !}

!!! note
    More integration examples you can find [here](../../integrations/1_integrations-index/)

??? tip "Don't forget to stop test broker container"
    ```bash
    docker container stop test-mq
    ```