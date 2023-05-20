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

**Propan** - just *~~an another one HTTP~~* a **declarative Python MQ framework**. It's following by <a href="https://fastapi.tiangolo.com/ru/" target="_blank">*fastapi*</a>, simplify Message Brokers around code writing and provides a helpful development toolkit, which existed only in HTTP-frameworks world until now.

It's designed to create reactive microservices around <a href="https://microservices.io/patterns/communication-style/messaging.html" target="_blank">Messaging Architecture</a>.

It is a modern, high-level framework on top of popular specific Python brokers libraries, based on <a href="https://docs.pydantic.dev/" target="_blank">*pydantic*</a> and <a href="https://fastapi.tiangolo.com/ru/" target="_blank">*fastapi*</a>, <a href="https://docs.pytest.org/en/7.3.x/" target="_blank">*pytest*</a> concepts.

---

**Documentation**: <a href="https://lancetnik.github.io/Propan/" target="_blank">https://lancetnik.github.io/Propan/</a>

---

### The key features are

* **Simple**: Designed to be easy to use and learn.
* **Intuitive**: Great editor support. Autocompletion everywhere.
* [**Dependencies management**](#dependencies): Minimization of code duplication. Access to dependencies at any level of the call stack.
* [**Integrations**](#http-frameworks-integrations): **Propan** is fully compatible with <a href="https://lancetnik.github.io/Propan/integrations/1_integrations-index/" target="_blank">any HTTP framework</a> you want
* **MQ independent**: Single interface to popular MQ:
  * **Redis** (based on <a href="https://redis.readthedocs.io/en/stable/index.html" target="_blank">redis-py</a>)
  * **RabbitMQ** (based on <a href="https://aio-pika.readthedocs.io/en/latest/" target="_blank">aio-pika</a>)
  * **NATS** (based on <a href="https://github.com/nats-io/nats.py" target="_blank">nats-py</a>)
* <a href="https://lancetnik.github.io/Propan/getting_started/4_broker/5_rpc/" target="_blank">**RPC**</a>: The framework supports RPC requests over MQ, which will allow performing long operations on remote services asynchronously.
* [**Great to develop**](#cli-power): CLI tool provides great development experience:
  * framework-independent way to manage the project environment
  * application code *hot reload*
  * robust application templates
* <a href="https://lancetnik.github.io/Propan/getting_started/7_testing" target="_blank">**Testability**</a>: **Propan** allows you to test your app without external dependencies: you do not have to set up a Message Broker, you can use a virtual one!

### Supported MQ brokers

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

### Community

If you are interested in this project, please give me feedback by star or/and watch repository.

If you have any questions or ideas about features to implement, welcome to [discussions](https://github.com/Lancetnik/Propan/discussions) or public [telegram group](https://t.me/propan_python).

---

## Declarative?

With declarative tools you can define **what you need to get**. With traditional imperative tools you must write **what you need to do**.

Take a look at classic imperative tools, such as <a href="https://aio-pika.readthedocs.io/en/latest/" target="_blank">aio-pika</a>, <a href="https://pika.readthedocs.io/en/stable/" target="_blank">pika</a>, <a href="https://redis.readthedocs.io/en/stable/index.html" target="_blank">redis-py</a>, <a href="https://github.com/nats-io/nats.py" target="_blank">nats-py</a>, etc.

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

## Quickstart

Install using `pip`:

```shell
pip install "propan[async-rabbit]"
# or
pip install "propan[async-nats]"
# or
pip install "propan[async-redis]"
```

### Basic usage

Create an application with the following code at `serve.py`:

```python
from propan import PropanApp
from propan import RabbitBroker
# from propan import RedisBroker
# from propan import NatsBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
# broker = NatsBroker("nats://localhost:4222")
# broker = RedisBroker("redis://localhost:6379")

app = PropanApp(broker)

@broker.handle("test")
async def base_handler(body):
    '''Handle all default exchange messages with `test` routing key'''
    print(body)
```

And just run it:

```shell
propan run serve:app
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
If you call not existing field, raises *pydantic.ValidationError* value.

But you can specify your own dependencies, call dependencies functions (like `Fastapi Depends`)
and [more](https://github.com/Lancetnik/Propan/tree/main/examples/dependencies).

```python
import aio_pika
from propan import PropanApp, RabbitBroker, Context, Depends

rabbit_broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(rabbit_broker)

async def dependency(body: dict) -> bool:
    return True

@rabbit_broker.handle("test")
async def base_handler(body: dict,
                       dep: bool = Depends(dependency),
                       broker: RabbitBroker = Context()):
    assert dep is True
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
propan run serve:app --env=.env.dev
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
    context.set_global("settings", settings)
```

### Project template

Also, **Propan CLI** is able to generate a production-ready application template:

```bash
propan create async rabbit [projectname]
```

*Notice: project template require* `pydantic[dotenv]` *installation.*

Run the created project:

```bash
# Run rabbimq first
docker compose --file [projectname]/docker-compose.yaml up -d

# Run project
propan run [projectname].app.serve:app --env=.env --reload
```

Now you can enjoy a new development experience!

---

## HTTP Frameworks integrations

### Any Framework

You can use **Propan** `MQBrokers` without `PropanApp`.
Just *start* and *stop* them according to your application lifespan.

```python
from propan import NatsBroker
from sanic import Sanic

app = Sanic("MyHelloWorldApp")
broker = NatsBroker("nats://localhost:4222")

@broker.handle("test")
async def base_handler(body):
    print(body)

@app.after_server_start
async def start_broker(app, loop):
    await broker.start()

@app.after_server_stop
async def stop_broker(app, loop):
    await broker.close()
```

### FastAPI Plugin

Also, **Propan** can be used as part of **FastAPI**.

Just import a **PropanRouter** you need and declare the message handler
using the `@event` decorator. This decorator is similar to the decorator `@handle` for the corresponding brokers.

```python
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from propan.fastapi import RabbitRouter

app = FastAPI()

router = RabbitRouter("amqp://guest:guest@localhost:5672")

class Incoming(BaseModel):
    m: dict

def call():
    return True

@router.event("test")
async def hello(m: Incoming, d = Depends(call)) -> dict:
    return { "response": "Hello, Propan!" }

app.include_router(router)
```

## Examples

To see more framework usages go to [**examples/**](https://github.com/Lancetnik/Propan/tree/main/examples)
