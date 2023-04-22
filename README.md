<p align="center">
    <a href="https://lancetnik.github.io/Propan/" target="_blank">
        <img src="https://lancetnik.github.io/Propan/assets/img/logo-no-background.png" alt="Propan logo" style="height: 250px; width: 600px;"/>
    </a>
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

**Propan** - just *<s>an another one HTTP</s>* a **declarative Python MQ framework**. It's following by [*fastapi*](https://fastapi.tiangolo.com/ru/),
simplify Message Brokers around code writing and provides a helpful development toolkit, which existed only in HTTP-frameworks world until now.

It's designed to create reactive microservices around <a href="https://microservices.io/patterns/communication-style/messaging.html" target="_blank">Messaging Architecture</a>.

It is a modern, high-level framework on top of popular specific Python brokers libraries, based on [*pydantic*](https://docs.pydantic.dev/) and [*fastapi*](https://fastapi.tiangolo.com/ru/), [*pytest*](https://docs.pytest.org/en/7.3.x/) concepts.

---

**Documentation**: <a href="https://lancetnik.github.io/Propan/" target="_blank">https://lancetnik.github.io/Propan/</a>

**Sources**: <a href="https://github.com/Lancetnik/Propan/" target="_blank">https://github.com/Lancetnik/Propan/</a>

---

### The key features are

* **Easy**: Designed to be easy to use and learn.
* **Intuitive**: Great editor support. Autocompletion everywhere.
* [**Dependencies management**](#dependencies): Minimize code duplication. Multiple features from each argument and parameter declaration.
* [**Integrations**](#http-frameworks-integrations): **Propan** is ready to use in pair with [any HTTP framework](https://lancetnik.github.io/Propan/5_integrations/1_integrations-index/) you want
* **MQ independent**: Single interface to popular MQ:
    * **NATS** (based on [nats-py](https://github.com/nats-io/nats.py)) 
    * **RabbitMQ** (based on [aio-pika](https://aio-pika.readthedocs.io/en/latest/)) 
* [**Greate to develop**](#cli-power): CLI tool provides great development experience:
    * framework-independent way to rule application environment
    * application code hot reloading

### Supported MQ brokers
|              | async                                                   | sync                 |
|--------------|:-------------------------------------------------------:|:--------------------:|
| **RabbitMQ** | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Nats**     | :warning: **beta** :warning:                            | :mag: planning :mag: |
| **NatsJS**   | :hammer_and_wrench: **in progress** :hammer_and_wrench: | :mag: planning :mag: |
| **MQTT**     | :mag: planning :mag:                                    | :mag: planning :mag: |
| **REDIS**    | :mag: planning :mag:                                    | :mag: planning :mag: |
| **Kafka**    | :mag: planning :mag:                                    | :mag: planning :mag: |
| **SQS**      | :mag: planning :mag:                                    | :mag: planning :mag: |


### Community

If you are interested in this project, please give me feedback by star or/and watch repository.

If you have any questions or ideas about features to implement, welcome to [discussions](https://github.com/Lancetnik/Propan/discussions) or public [telegram group](https://t.me/propan_python).

---

## Declarative?

With declarative tools you should define **what you need to get**. With traditional imperative tools you should write **what you need to do**.

Take a look at classic imperative tools, such as [aio-pika](https://aio-pika.readthedocs.io/en/latest/), [pika](https://pika.readthedocs.io/en/stable/), [nats-py](https://github.com/nats-io/nats.py), etc. 

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

**aio-pika** is a really great tool with a really easy learning curve. But it's still imperative. You need to *connect*, declare *channel*, *queues*, *exchanges* by yourself. Also, you need to manage *connection*, *message*, *queue* context to avoid any troubles.

It is not a bad way, but it can be easy.

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

## Quickstart

Install using `pip`:

```shell
$ pip install "propan[async-rabbit]"
# or
$ pip install "propan[async-nats]"
```

### Basic usage

Create an application with the following code at `serve.py`:

```python
from propan import PropanApp
from propan import RabbitBroker
# from propan import NatsBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
# broker = NatsBroker("nats://localhost:4222")

app = PropanApp(broker)

@broker.handle("test")
async def base_handler(body):
    '''Handle all default exchange messages with `test` routing key'''
    print(body)
```

And just run it:

```shell
$ propan run serve:app
```

---

## Type casting

Propan uses `pydantic` to cast incoming function arguments to types according to their annotation.

```python
from pydantic import BaseModel
from propan import PropanApp, Context, RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(broker)

class SimpleMessage(BaseModel):
    key: int

@broker.handle("test2")
async def second_handler(body: SimpleMessage):
    assert isinstance(body.key, int)

```

---

## Dependencies

**Propan** a has dependencies management policy close to `pytest fixtures`.
You can specify in functions arguments which dependencies
you would to use. Framework passes them from the global Context object.

Already existed context fields are: *app*, *broker*, *context* (itself), *logger* and *message*.
If you call not existing field, raises *pydantic.error_wrappers.ValidationError* value.

But you can specify your own dependencies, call dependencies functions (like `Fastapi Depends`)
and [more](https://github.com/Lancetnik/Propan/tree/main/examples/dependencies).

```python
from logging import Logger

import aio_pika
from propan import PropanApp, Context, RabbitBroker

rabbit_broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(rabbit_broker)

@rabbit_broker.handle("test")
async def base_handler(body: dict,
                       broker: RabbitBroker = Context()):
    assert broker is rabbit_broker
```

---

## CLI power

**Propan** has its own CLI tool that provided the following features:
* project generation
* multiprocessing workers
* project hot reloading
* custom command line arguments passing

### Context passing

For example: pass your current *.env* project setting to context
```bash
$ propan run serve:app --env=.env.dev
```

```python
from propan import PropanApp, RabbitBroker
from propan.annotations import ContextRepo
from pydantic import BaseSettings

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

class Settings(BaseSettings):
    ...

@app.on_startup
async def setup(env: str, context: ContextRepo):
    settings = Settings(_env_file=env)
    context.set_context("settings", settings)
```

### Project template

Also, **Propan CLI** is able to generate a production-ready application template:

```shell
$ propan create [projectname]
```

*Notice: project template require* `pydantic[dotenv]` *installation.*

Run the created project:

```shell
# Run rabbimq first
$ docker compose --file [projectname]/docker-compose.yaml up -d

# Run project
$ propan run [projectname].app.serve:app --env=.env --reload
```

Now you can enjoy a new development experience!

---

## HTTP Frameworks integrations

You can use **Propan** `MQBrokers` without `PropanApp`.
Just *start* and *stop* them according to your application lifespan.

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from propan import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()
    yield
    await broker.close()

@broker.handle("test")
async def base_handler(body):
    print(body)
```

## Examples

To see more framework usages go to [**examples/**](https://github.com/Lancetnik/Propan/tree/main/examples)
