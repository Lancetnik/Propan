<p align="center">
    <img src="docs/files/logo-no-background.png" alt="Propan logo" style="height: 250px; width: 600px;"/>
</p>

<p align="center">
    <a href="https://github.com/Lancetnik/Propan/actions/workflows/tests.yml" target="_blank">
        <img src="https://github.com/Lancetnik/Propan/actions/workflows/tests.yml/badge.svg" alt="Tests coverage"/>
    </a>
    <a href="https://smokeshow.helpmanual.io/2p3n1z2c5q39130x176i/" target="_blank">
        <img src="docs/files/coverage.svg" alt="Tests coverage"/>
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

Propan is a modern framework for building Applications based on <a href="https://microservices.io/patterns/communication-style/messaging.html" target="_blank">Messaging Architecture</a>.

The key features are:

* **Easy**: Designed to be easy to use and learn.
* **Intuitive**: Great editor support. Autocompletion everywhere.
* [**Dependencies management**](#dependencies): Minimize code duplication. Multiple features from each argument and parameter declaration.
* [**Integrations**](#http-frameworks-integrations): Propan is ready to using in pair with [any http framework](https://github.com/Lancetnik/Propan/tree/main/examples/http_frameworks_integrations) you want
* **MQ independent**: Single interface to popular MQ:
    * **NATS** (based on [nats-py](https://github.com/nats-io/nats.py)) 
    * **RabbitMQ** (based on [aio-pika](https://aio-pika.readthedocs.io/en/latest/)) 
* [**Greate to develop**](#cli-power): cli tool provides great development expireince:
    * framework-independent way to rule application environment
    * application code hot reloading

Supported MQ brokers:
| Broker       | async                                                   | sync                 |
|--------------|:-------------------------------------------------------:|:--------------------:|
| **RabbitMQ** | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Nats**     | :warning: **beta** :warning:                            | :mag: planning :mag: |
| **NatsJS**   | :hammer_and_wrench: **in progress** :hammer_and_wrench: | :mag: planning :mag: |
| **Kafka**    | :mag: planning :mag:                                    | :mag: planning :mag: |

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
from propan.brokers.rabbit import RabbitBroker
# from propan.brokers.nats import NatsBroker

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

Propan uses `pydantic` to cast incoming function arguments to type according their type annotation.

```python
from pydantic import BaseModel
from propan import PropanApp, Context
from propan.brokers.rabbit import RabbitBroker

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

Propan has dependencies management policy close to `pytest fixtures`.
You can specify in functions arguments which dependencies
you would to use. Framework passes them from the global Context object.

Default context fields are: *app*, *broker*, *context* (itself), *logger* and *message*.
If you call not existed field it returns *None* value.

But you can specify your own dependencies, call dependencies functions (like `Fastapi Depends`)
and [more](https://github.com/Lancetnik/Propan/tree/main/examples/dependencies).

```python
from logging import Logger

import aio_pika
from propan import PropanApp, Context
from propan.brokers.rabbit import RabbitBroker

rabbit_broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(rabbit_broker)

@rabbit_broker.handle("test")
async def base_handler(body: dict,
                       app: PropanApp,
                       broker: RabbitBroker,
                       context: Context,
                       logger: Logger,
                       message: aio_pika.Message,
                       not_existed_field):
    assert broker is rabbit_broker
    assert not_existed_field is None
```

---

## CLI power

Propan has own cli tool providing following features:
* project generation
* multiprocessing workers
* project hot reloading
* custom context arguments passing

### Context passing

For example: pass your current *.env* project setting to context
```bash
$ propan run serve:app --env=.env.dev
```

```python
from propan import PropanApp, Context
from propan.brokers.rabbit import RabbitBroker
from pydantic import BaseSettings

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

class Settings(BaseSettings):
    ...

@app.on_startup
async def setup(env: str, context: Context):
    settings = Settings(_env_file=env)
    context.set_context("settings", settings)
```

### Project template

Also **propan cli** is able to generate production-ready application template:

```shell
$ propan create [projectname]
```

*Notice: project template require* `pydantic[dotenv]` *installation.*

Run created project:

```shell
# Run rabbimq first
$ docker compose --file [projectname]/docker-compose.yaml up -d

# Run project
$ propan run [projectname].app.serve:app --env=.env --reload
```

Now you can enjoy a new development experience!

---

## HTTP Frameworks integrations

You can use Propan MQBrokers without PropanApp.
Just *start* and *stop* them according your application lifespan.

```python
from fastapi import FastAPI
from propan.brokers.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = FastAPI()

@broker.handle("test")
async def base_handler(body):
    print(body)

@app.on_event("startup")
async def start_broker():
    await broker.start()

@app.on_event("shutdown")
async def stop_broker():
    await broker.close()
```

## Examples

To see more framework usages go to [**examples/**](https://github.com/Lancetnik/Propan/tree/main/examples)
