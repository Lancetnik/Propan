---
icon: material/information
---

# Migration to **FastStream**

**Propan** project is superceeded by [**FastStream**](https://github.com/airtai/faststream){.external-link target="_blank"}.

**FastStream** is a new package based on the ideas and experiences gained from [**FastKafka**](https://github.com/airtai/fastkafka){.external-link targer="_blank"} and **Propan**. By joining our forces, we picked up the best from both packages and created a unified way to write services capable of processing streamed data regardless of the underlying protocol.

I’ll continue to maintain **Propan** package, but new development will be in **FastStream**. If you are starting a new service, **FastStream** is the recommended way to do it.

For now **FastStream** supports **Kafka** and **RabbitMQ**. Other brokers support will be added in a few months.

## Migration

Your current **Propan** application should work with the **FastStream** as well. You just need to change a few lines of code:

* Replace your `PropanApp` instance with `FastStream` one
* replace all `#!python @broker.hanler(...)` usages to `#!python @broker.subscriber(...)`
* change broker imports to `fasttream.rabbit`, `faststream.kafka`, e.t.c.

Also, if you are using **RPC**-supporting brokers, you should mv all `#!python broker.publish(..., callback=True)` calls to `#!python broker.publish(..., rpc=True)`.

And so the job is done! Your **Propan** application was migrated to the **FastStream**!

## Removed features

Unfortunately, during the development of **FastStream**, some features were removed, namely:

* template generation
* **Kafka-RPC** (and **SQS** in future) requests

Now the project templates will be implemented in a separate repository and distributed via [**cookiecutter**](https://cookiecutter.readthedocs.io/en/stable/){.external-docs targer="_blank"}.

In the case of **RPC** requests, it was a mistake to claim that we would be able to support their implementation through a unified syntax. Support for **RPC** in brokers that were not designed for such functionality (for example, **Kafka** and **SQS**) was implemented in a poorly scalable way, and the high-level syntax hid implementation flaws from the user. Now you will have to implement this functionality yourself, but in the documentation, you will find a detailed guide on how to do it.

## Added Features

**FastStream** contains many additional features. Here is a short list of them:

**Multiple subscription**

:   Now you can subscribe one function to many different message sources
    ```python
    @broker.subscriber("stream1")
    @broker.subscriber("stream2")
    async def handler(msg): ...
    ```

**Application level filters**

:   You can declare multiple handlers for your message flow and determine which one to use right at the application level
    ```python
    @broker.subscriber(
        "stream",
        filter=lambda msg: msg.content_type == "application/json",
    )
    async def json_handler(msg): ...

    @broker.subscriber("stream")
    async def default_handler(msg): ...
    ```

**Structured publishers**

:   **FastStream** contains a fundamentally new decorator - `#!python @broker.publisher(...)`, which allows you to describe your services as structured stages of message processing, as well as display outgoing flows in the **AsyncAPI** schema
    ```python
    @broker.subscriber("in-stream")
    @broker.publisher("out-stream")
    async def handler(msg): ...
    ```

And also:

* new testing features (testable lifespans, publisher and subscriber mock objects)
* better customization: decoders, new middleware
* better **AsyncAPI** support
* performance improvement

But the most important difference is that now there is a whole **AirtAI** team behind the framework (and me), so you will get the best support and maintenance of the framework!
