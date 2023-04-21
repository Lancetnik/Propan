# CHANGELOG 

## **0.0.9** 2023-04-18

Release is timed to accompany the release of [fast-depends](https://lancetnik.github.io/FastDepends/).
Now it's used as the **Propan** Dependency Injection system deep inside. Context is an *fast-depends CustomField* child now.

## Features:
* Deep `Depends` nesting
* More flexable `Context` behavior
* Full tested and stable decorating system
* Add `propan.annotation` module to faster access to already declared context fields

## Breaking changes
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

## Breaking changes

## **2023-04-05 Propan INITIAL**
Hello there! Congratulate everybody and me with the first stable *Propan* release!

## Release features:
### Stable
* async RabbitMQ broker
* depedencies injection features
* type casting
* CLI tool

### Experimental
As an experimental feature in this release was added *NATS* (not Jetstream) supporting.

## Next steps
* Full NATS supporting (with Jetstream)
* Syncronous version of all brokers and app
* Kafka brokers
