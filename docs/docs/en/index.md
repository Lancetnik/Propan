<p align="center">
    <img src="assets/img/logo-no-background.png" alt="Propan logo" style="height: 250px; width: 600px;"/>
</p>

<p align="center">
    <a href="https://github.com/Lancetnik/Propan/actions/workflows/tests.yml" target="_blank">
        <img src="https://github.com/Lancetnik/Propan/actions/workflows/tests.yml/badge.svg" alt="Tests coverage"/>
    </a>
    <a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/lancetnik/propan" target="_blank">
        <img src="https://coverage-badge.samuelcolvin.workers.dev/lancetnik/propan.svg" alt="Coverage">
    </a>
    <a href="https://pypi.org/project/propan" target="_blank">
        <img src="https://img.shields.io/pypi/v/propan?label=pypi%20package" alt="Package version">
    </a>
    <a href="https://pepy.tech/project/propan" target="_blank">
        <img src="https://static.pepy.tech/personalized-badge/propan?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads" alt="downloads"/>
    </a>
    <br/>
    <a href="https://pypi.org/project/propan" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/propan.svg" alt="Supported Python versions">
    </a>
    <a href="https://github.com/Lancetnik/Propan/blob/main/LICENSE" target="_blank">
        <img alt="GitHub" src="https://img.shields.io/github/license/Lancetnik/Propan?color=%23007ec6">
    </a>
    <a href="https://discord.gg/ChhMXJpvz7" target="_blank">
        <img alt="Discord" src="https://img.shields.io/discord/1122560426794831872?logo=discord">
    </a>
</p>

# Propan

**Propan** - just *<s>another HTTP</s>* a **declarative Python Messaging framework**.

Inspired by [*FastAPI*]({{ urls.fastapi }}){target="_blank"} and [*Kombu*]({{ urls.kombu }}){target="_blank"}, **Propan** was created to simplify Message Brokers' code writing and to provide a helpful development toolkit, which existed only in HTTP-frameworks world until now.

It's designed to create reactive microservices around [Messaging](https://microservices.io/patterns/communication-style/messaging.html){target="_blank"}.

It is a modern, high-level framework on top of popular specific Python brokers libraries, based on [*pydantic*]({{ urls.pydantic }}){target="_blank"}, [*FastAPI*]({{ urls.fastapi }}){target="_blank"}, and [*pytest*]({{ urls.pytest }}){target="_blank"} concepts.

---

## :warning::warning::warning: Deprecation notice :warning::warning::warning:

**Propan** project is superceeded by [**FastStream**](https://github.com/airtai/faststream){.external-link target="_blank"}.

**FastStream** is a new package based on the ideas and experiences gained from [**FastKafka**](https://github.com/airtai/fastkafka){.external-link targer="_blank"} and **Propan**. By joining our forces, we picked up the best from both packages and created a unified way to write services capable of processing streamed data regardless of the underlying protocol.

I’ll continue to maintain **Propan** package, but new development will be in **FastStream**. If you are starting a new service, **FastStream** is the recommended way to do it.

For now **FastStream** supports **Kafka** and **RabbitMQ**. Other brokers support will be added in a few months.

You can find a detail migration guide in the [documentation](./migration.md){.internal-link}

---

## The key features are

* **Simple**: Designed to be easy to use and learn.
* **Intuitive**: Great editor support. Autocompletion everywhere.
* [**Dependencies management**](getting_started/1_quick-start/#dependencies): Minimization of code duplication. Access to dependencies at any level of the call stack.
* [**Integrations**](getting_started/1_quick-start/#http-frameworks-integrations): **Propan** is fully compatible with [any HTTP framework](integrations/1_integrations-index/) you want
* **MQ independent**: Single interface to popular MQ:
    * **Redis** (based on [redis-py]({{ urls.redis }}){target="_blank"})
    * **RabbitMQ** (based on [aio-pika]({{ urls.aio_pika }}){target="_blank"})
    * **Kafka** (based on [aiokafka]({{ urls.aiokafka }}){target="_blank"})
    * **SQS** (based on [aiobotocore]({{ urls.aiobotocore }}){target="_blank"})
    * **Nats** (based on [nats-py]({{ urls.nats_py }}){target="_blank"})
* [**RPC**](getting_started/4_broker/5_rpc/): The framework supports RPC requests on top of message brokers, which will allow performing long operations on remote services asynchronously.
* [**Great to develop**](getting_started/2_cli/): CLI tool provides great development experience:
    * framework-independent way to manage the project environment
    * application code *hot reload*
    * robust application templates
* [**Documentation**](getting_started/9_documentation/): **Propan** automatically generates and presents an interactive [**AsyncAPI**]({{ urls.asyncapi }}){target="_blank"} documentation for your project
* [**Testability**](getting_started/7_testing): **Propan** allows you to test your app without external dependencies: you do not have to set up a Message Broker, you can use a virtual one!

---

## Declarative

With declarative tools you can define **what you need to get**. With traditional imperative tools you must write **what you need to do**.

Take a look at classic imperative tools, such as [aio-pika]({{ urls.aio_pika }}){target="_blank"}, [pika]({{ urls.pika }}){target="_blank"}, [redis-py]({{ urls.redis }}){target="_blank"}, [nats-py]({{ urls.nats_py }}){target="_blank"}, [aiokafka]({{ urls.aiokafka }}){target="_blank"}, etc.

This is the **Quickstart** with the *aio-pika*:

```python
import asyncio
import aio_pika

async def main():
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/"
    )

    queue_name = "test_queue"

    async with connection:
        channel = await connection.channel()

        queue = await channel.declare_queue(queue_name)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(message.body)

asyncio.run(main())
```

**aio-pika** is a great tool with a really easy learning curve. But it's still imperative. You need to *connect*, declare *channel*, *queues*, *exchanges* by yourself. Also, you need to manage *connection*, *message*, *queue* context to avoid any troubles.

It is not a bad way, but it can be much easier.

```python
from propan import PropanApp, RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

@broker.handle("test_queue")
async def base_handler(body):
    print(body)
```

This is the **Propan** declarative way to write the same code. That is so much easier, isn't it?

---

## Type casting

Propan uses `pydantic` to cast incoming function arguments to types according to their annotation.

```python linenums="1" hl_lines="5 9"
{!> docs_src/index/02_type_casting.py!}
```

---

## Dependencies

**Propan** has a dependencies management policy close to `pytest fixtures` and `FastAPI Depends` at the same time.
Function arguments declare which dependencies you want are needed, and a special decorator delivers them from the global Context object.

Already declared context fields are: *app*, *broker*, *context* (itself), *logger* and *message*.
If you call a non-existent field, raises *pydantic.error_wrappers.ValidationError* value.

But you can specify your own dependencies, call dependencies functions and [more](../5_dependency/1_di-index).

```python linenums="1" hl_lines="11-12"
{!> docs_src/index/03_dependencies.py!}
```

---

## Project Documentation

**Propan** automatically generates documentation for your project according to the [**AsyncAPI**]({{ urls.asyncapi }}){ target="_blank"} specification. You can work with both generated artifacts and place a Web view of your documentation on resources available to related teams.

The availability of such documentation significantly simplifies the integration of services: you can immediately see what channels and message format the application works with. And most importantly, it won't cost anything - **Propan** has already created the docs for you!

![HTML-page](../../assets/img/docs-html-short.png)

---

## HTTP Frameworks integrations

### Any Framework

You can use **Propan** `MQBrokers` without `PropanApp`.
Just *start* and *stop* them according to your application lifespan.

{! includes/getting_started/index/04_http_example.md !}

### **FastAPI** Plugin

Also, **Propan** can be used as part of **FastAPI**.

Just import a **PropanRouter** you need and declare the message handler
using the `@event` decorator. This decorator is similar to the decorator `@handle` for the corresponding brokers.

!!! tip
    When used this way, **Propan** does not utilize its own dependency system, but integrates into **FastAPI**.
    That is, you can use `Depends`, `BackgroundTasks` and other tools **FastAPI** as if it were a regular HTTP endpoint.

{! includes/getting_started/index/05_native_fastapi.md !}

!!! note
    More integration examples can be found [here](integrations/1_integrations-index/)

---

## Supported MQ brokers

!!! note "Need your help"
    The framework is now in active development. We have a very long list of what has yet to be implemented and various brokers are only part of it. If you want to implement something from this list or help in any other way, take a look [here](contributing/1_todo/)

|                   | async                                                   | sync                                        |
|-------------------|:-------------------------------------------------------:|:-------------------------------------------:|
| **RabbitMQ**      | :heavy_check_mark: **stable** :heavy_check_mark:        | :hammer_and_wrench: WIP :hammer_and_wrench: |
| **Redis**         | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag:                        |
| **Nats**          | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag:                        |
| **Kafka**         | :warning: **beta** :warning:                            | :mag: planning :mag:                        |
| **SQS**           | :warning: **beta** :warning:                            | :mag: planning :mag:                        |
| **NatsJS**        | :warning: **beta** :warning:                            | :mag: planning :mag:                        |
| **ZeroMQ**        | :hammer_and_wrench: WIP :hammer_and_wrench:             | :mag: planning :mag:                        |
| **MQTT**          | :mag: planning :mag:                                    | :mag: planning :mag:                        |
| **Redis Streams** | :mag: planning :mag:                                    | :mag: planning :mag:                        |
| **Pulsar**        | :mag: planning :mag:                                    | :mag: planning :mag:                        |
| **ActiveMQ**      | :mag: planning :mag:                                    | :mag: planning :mag:                        |
| **AzureSB**       | :mag: planning :mag:                                    | :mag: planning :mag:                        |