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

**Propan** - just *<s>another one HTTP</s>* a **declarative Python MQ framework**. It it inspired by [*fastapi*]({{ urls.fastapi }}){target="_blank"}, aims to simplify writing code that works with Message Brokers and provides a helpful development toolkit, which existed only in HTTP-frameworks world until now.

It's designed to create reactive microservices around [Messaging](https://microservices.io/patterns/communication-style/messaging.html){target="_blank"}.

It is a modern, high-level framework on top of popular Python libraries for various message brokers, based on [*pydantic*]({{ urls.pydantic }}){target="_blank"} and [*fastapi*]({{ urls.fastapi }}){target="_blank"}, [*pytest*]({{ urls.pytest }}){target="_blank"} concepts.

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

## Supported MQ brokers

!!! note "Need your help"
    The framework is now in active development. We have a very long list of what has yet to be implemented and various brokers are only part of it. If you want to implement something from this list or help in any other way, take a look [here](contributing/1_todo/)

|                   | async                                                   | sync                 |
|-------------------|:-------------------------------------------------------:|:--------------------:|
| **RabbitMQ**      | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Redis**         | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Nats**          | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Kafka**         | :warning: **beta** :warning:                            | :mag: planning :mag: |
| **SQS**           | :warning: **beta** :warning:                            | :mag: planning :mag: |
| **NatsJS**        | :hammer_and_wrench: **in progress** :hammer_and_wrench: | :mag: planning :mag: |
| **MQTT**          | :mag: planning :mag:                                    | :mag: planning :mag: |
| **Redis Streams** | :mag: planning :mag:                                    | :mag: planning :mag: |
| **Pulsar**        | :mag: planning :mag:                                    | :mag: planning :mag: |