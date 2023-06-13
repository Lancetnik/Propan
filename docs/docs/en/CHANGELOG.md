# CHANGELOG

## 2023-06-13 **0.1.2.17**

The current update is a sum of several changes and improvements released from the previous release.

The main change - **Propan** no longer obliges you to receive a message in the form of only one argument.
Your handler function can consume as many arguments as needed and also combine them with **pydantic.BaseModel**.

```python
@router.handle(...)
async def handler(a: int, b: float):
...
async def handler(a: Message, b: float, c: str):
```

A few public methods for declaring objects **RabbitMQ** were added to **RabbitBroker**:

```python
broker = RabbitBroker()
...
     await broker.declare_exchange(RabbitExchange("test"))
     await broker.declare_queue(RabbitQueue("test"))
     channel: aio_pika.RobustChannel = broker.channel
```

To maintain the ability to send messages and initialize channels, an `after_startup` hook has been added to all **FastAPI PropanRouters**.

```python
router = RabbitRouter()

@router.after_startup
async def init_whatever(app: FastAPI): ...
```

In addition, the behavior of the `__init__` and `connect` methods for all brokers have been improved (now the `connect` parameters have priority and override the `__init__` parameters when connecting to the broker), a correct exception has been implemented when accessing an object unavailable for import, several errors have been fixed and other minor internal changes.

## 2023-05-28 **0.1.2.3** SQS Beta

**Propan** added support for *SQS* as a message broker. This functionality is full tested.

*SQSBroker* supports:

* message delivery
* test client, without the need to run *ElasticMQ* or connect to cloud *SQS*
* *FastAPI* Plugin

*SQSBroker* not supports **RPC** yet.

Also, current release include the following fixes:

* *Kafka* connection recovery
* *Nats* connection recovery
* *Redis* connection methods supports not-url parameters

## 2023-05-26 **0.1.2.2** NATS Stable

`NatsBroker` is full tested now.

Also, to **Nats** supporting added:

* `TestNatsBroker` and test messages to local testing
* **RPC** supporting
* `NatsRouter` for **FastAPI**

## 2023-05-23 **0.1.2.0** Kafka

**Propan** added support for *Kafka* as a message broker. This functionality is full tested.

*KafkaBroker* supports:

* message delivery
* test client, without the need to run *Kafka*
* *FastAPI* Plugin

*KafkaBroker* not supports **RPC** yet.

## 2023-05-18 **0.1.1.0** REDIS

**Propan** added support for *Redis Pub/Sub* as a message broker. This functionality is full tested and described in the documentation.

*RedisBroker* supports:

* message delivery by key or pattern
* test client, without the need to run *Redis*
* **RPC** requests over *Redis Pub/Sub*
* *FastAPI* Plugin

Also, **Propan CLI** is able to generate templates to any supported broker

```bash
propan create async [broker] [APPNAME]
```

## 2023-05-15 **0.1.0.0** STABLE

Stable and fully documented **Propan** release!

From the current release, no more breaking changes - use the framework safely!

At the current release, all *RabbitMQ* use cases are supported, tested, and described in the documentation.
Expect support for *Redis* (testing now), *Kafka* (in development), and full support for *Nats* (also in development) soon.

## 2023-05-01 **0.0.9.4**

Great news! Now **Propan** can be used as a full part of **FastAPI**!

```python
from fastapi import FastAPI
from propan.fastapi import RabbitRouter

router = RabbitRouter("amqp://guest:guest@localhost:5672")

app = FastAPI(lifespan=router.lifespan_context)

@router.event("test")
async def hello(m: dict) -> dict:
     return { "response": "Hello Propan!" }

app.include_router(router)
```

You can find a complete example in [documentation](../integrations/2_fastapi-plugin)

Also, added the ability to [test](../getting_started/7_testing) your application without running external dependencies as a broker (for now only for RabbitMQ)!

```python
from propan import RabbitBroker
from propan.test import TestRabbitBroker

broker = RabbitBroker()

@broker.handler("ping")
async def healthcheck(msg: str) -> str:
     return "pong"

def test_publish():
     async with TestRabbitBroker(broker) as test_broker:
         await test_broker.start()
         r = await test_broker.publish("ping", queue="ping", callback=True)
     assert r == "pong"
```

Also added support for [RPC over MQ](../getting_started/4_broker/5_rpc) (RabbitMQ only for now): `return` of your handler function will be sent in response to a message if a response is expected.

<h3>Breaking changes:</h3>

* Brokers `publish_message` method has been renamed to `publish`
* removed `declare` argument in `RabbitQueue` and `RabbitExchange` - now you need to use `passive`

## 2023-04-18 **0.0.9**

Release is timed to accompany the release of [fast-depends](https://lancetnik.github.io/FastDepends/).
Now it's used as the **Propan** Dependency Injection system deep inside. Context is an *fast-depends CustomField* child now.

<h3>Features:</h3>

* Deep `Depends` nesting
* More flexable `Context` behavior
* Full tested and stable decorating system
* Add `propan.annotation` module to faster access to already declared context fields

<h3>Breaking changes</h3>

* `@use_context` was removed. Use `@apply_types` to solve `Context` now
* `Alias` was merged with the `Context` field
* Access to context fields is not granted by function arguments decalration anymore

Now you should use the following code:

```python
from propan import Context, apply_types
@apply_types
def func(logger = Context()): ...

# or
from propan import Context, apply_types
@apply_types
def func(l = Context("logger")): ...

# or
from propan import apply_types
from propan.annotations import Logger
@apply_types
def func(logger: Logger): ...
```

---

## 2023-04-05 **INITIAL**

Hello there! Congratulate everybody and me with the first stable *Propan* release!

<h3>Release features:</h3>
<h4>Stable</h4>

* async RabbitMQ broker
* depedencies injection features
* type casting
* CLI tool

<h4>Experimental</h4>
As an experimental feature in this release was added *NATS* (not Jetstream) supporting.

<h4>Next steps</h4>

* Full NATS supporting (with Jetstream)
* Syncronous version of all brokers and app
* Kafka brokers
