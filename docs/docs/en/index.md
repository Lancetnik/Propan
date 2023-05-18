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
</p>

# Propan

**Propan** - just *<s>another one HTTP</s>* a **declarative Python MQ framework**. It it inspired by [*fastapi*](https://fastapi.tiangolo.com/ru/){target="_blank"}, aims to simplify writing code that works with Message Brokers and provides a helpful development toolkit, which existed only in HTTP-frameworks world until now.

It's designed to create reactive microservices around [Messaging](https://microservices.io/patterns/communication-style/messaging.html){target="_blank"}.

It is a modern, high-level framework on top of popular Python libraries for various message brokers, based on [*pydantic*](https://docs.pydantic.dev/){target="_blank"} and [*fastapi*](https://fastapi.tiangolo.com/ru/){target="_blank"}, [*pytest*](https://docs.pytest.org/en/7.3.x/){target="_blank"} concepts.

---

## The key features are

* **Simple**: Designed to be easy to use and learn.
* **Intuitive**: Great editor support. Autocompletion everywhere.
* [**Dependencies management**](getting_started/1_quick-start/#dependencies): Minimization of code duplication. Access to dependencies at any level of the call stack.
* [**Integrations**](getting_started/1_quick-start/#http-frameworks-integrations): **Propan** is fully compatible with [any HTTP framework](integrations/1_integrations-index/) you want
* **MQ independent**: Single interface to popular MQ:
    * **Redis** (based on [redis-py]("https://redis.readthedocs.io/en/stable/index.html"){target="_blank"})
    * **RabbitMQ** (based on [aio-pika](https://aio-pika.readthedocs.io/en/latest/){target="_blank"})
    * **NATS** (based on [nats-py](https://github.com/nats-io/nats.py){target="_blank"})
* [**RPC**](getting_started/4_broker/5_rpc/): The framework supports RPC requests on top of message brokers, which will allow performing long operations on remote services asynchronously.
* [**Greate to develop**](getting_started/2_cli/): CLI tool provides great development experience:
    * framework-independent way to manage the project environment
    * application code *hot reload*
    * robust application templates
* [**Testability**](getting_started/7_testing): **Propan** allows you to test your app without external dependencies: you do not have to set up a Message Broker, you can use a virtual one!

---

## Declarative

With declarative tools you can define **what you need to get**. With traditional imperative tools you must write **what you need to do**.

Take a look at classic imperative tools, such as [aio-pika](https://aio-pika.readthedocs.io/en/latest/){target="_blank"}, [pika](https://pika.readthedocs.io/en/stable/){target="_blank"}, [redis-py]("https://redis.readthedocs.io/en/stable/index.html"){target="_blank"}, [nats-py](https://github.com/nats-io/nats.py){target="_blank"}, etc.

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

## Supported MQ brokers

!!! note "Need your help"
    The framework is now in active development. We have a very long list of what has yet to be implemented and various brokers are only part of it. If you want to implement something from this list or help in any other way, take a look [here](contributing/1_todo/)

|                   | async                                                   | sync                 |
|-------------------|:-------------------------------------------------------:|:--------------------:|
| **RabbitMQ**      | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Redis**         | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Nats**          | :warning: **beta** :warning:                            | :mag: planning :mag: |
| **NatsJS**        | :hammer_and_wrench: **in progress** :hammer_and_wrench: | :mag: planning :mag: |
| **MQTT**          | :mag: planning :mag:                                    | :mag: planning :mag: |
| **Kafka**         | :mag: planning :mag:                                    | :mag: planning :mag: |
| **Redis Streams** | :mag: planning :mag:                                    | :mag: planning :mag: |
| **Pulsar**        | :mag: planning :mag:                                    | :mag: planning :mag: |
| **SQS**           | :mag: planning :mag:                                    | :mag: planning :mag: |
