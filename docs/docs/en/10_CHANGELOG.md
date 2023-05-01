# CHANGELOG

## **0.0.9.4** 2023-05-01

Great news! Now **Propan** can be used as a full part of **FastAPI**!

```python
from fastapi import FastAPI
from propan.fastapi import RabbitRouter

app = FastAPI()

router = RabbitRouter("amqp://guest:guest@localhost:5672")

@router.event("test")
async def hello(m: dict) -> dict:
     return { "response": "Hello Propan!" }

app.include_router(router)
```

You can find a complete example in [documentation](../5_integrations/2_fastapi-plugin)

Also, added the ability to [test](../2_getting_started/7_testing) your application without running external dependencies as a broker (for now only for RabbitMQ)!

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

Also added support for [RPC over MQ](../2_getting_started/4_broker/5_rpc) (RabbitMQ only for now): `return` of your handler function will be sent in response to a message if a response is expected.

<h3>Breaking changes:</h3>

* Brokers `publish_message` method has been renamed to `publish`
* removed `declare` argument in `RabbitQueue` and `RabbitExchange` - now you need to use `passive`

## **0.0.9** 2023-04-18

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

## **INITIAL** 2023-04-05

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
