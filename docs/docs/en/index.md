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

Привет!

Propan is a modern framework for building Applications based on <a href="https://microservices.io/patterns/communication-style/messaging.html" target="_blank">Messaging Architecture</a>.

### The key features are

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

If you are interested at this project, please give me feedback by star or/and watch repository.

If you have any questions or ideas about features to implement, welcome to [discussions](https://github.com/Lancetnik/Propan/discussions) or publick [telegram group](https://t.me/propan_python).

---

## Quickstart

Install using `pip`:

=== "RabbitMQ"
    <div class="termy">
    ```console
    $ pip install "propan[async-rabbit]"
    ---> 100%

    ### Run test container
    docker run -d --rm -p 5672:5672 --name test-mq rabbitmq
    ```
    </div>

=== "NATS"
    <div class="termy">
    ```console
    $ pip install "propan[async-nats]"
    ---> 100%

    ### Run test container
    docker run -d --rm -p 4222:4222 --name test-mq nats
    ```
    </div>

### Basic usage

Create an application with the following code at `serve.py`:

=== "RabbitMQ"
    ```python
    {!> docs_src/index/01_rabbit_base.py!}
    ```

=== "NATS"
    ```python
    {!> docs_src/index/01_nats_base.py!}
    ```

And just run it:

<div class="termy">
```console
$ propan run serve:app

2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

---

## Type casting

Propan uses `pydantic` to cast incoming function arguments to type according their type annotation.

=== "RabbitMQ"
    ```python hl_lines="12"
    {!> docs_src/index/02_rabbit_type_casting.py!}
    ```

=== "NATS"
    ```python hl_lines="12"
    {!> docs_src/index/02_nats_type_casting.py!}
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

=== "RabbitMQ"
    ```python hl_lines="12-17"
    {!> docs_src/index/03_rabbit_dependencies.py!}
    ```

=== "NATS"
    ```python hl_lines="12-17"
    {!> docs_src/index/03_nats_dependencies.py!}
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
<div class="termy">
```console
$ propan run serve:app --env=.env.dev

2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

=== "RabbitMQ"
    ```python hl_lines="3 9 14-15"
    {!> docs_src/index/04_rabbit_context.py!}
    ```

=== "NATS"
    ```python hl_lines="3 9 14-15"
    {!> docs_src/index/04_nats_context.py!}
    ```

### Project template

Also **propan cli** is able to generate production-ready application template:

<div class="termy">
```console
$ propan create [projectname]
Create Propan project template at: /home/user/projectname
```
</div>

*Notice: project template require* `pydantic[dotenv]` *installation.*

Run created project:

<div class="termy">
```console
### Run rabbimq first
$ docker compose --file [projectname]/docker-compose.yaml up -d

### Run project
$ propan run [projectname].app.serve:app --env=.env --reload

2023-04-10 23:39:41,140 INFO     - Started reloader process [115536] using WatchFiles
2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

Now you can enjoy a new development experience!

---

## HTTP Frameworks integrations

You can use Propan MQBrokers without PropanApp.
Just *start* and *stop* them according your application lifespan.

=== "RabbitMQ"
    ```python hl_lines="12-14 16-18"
    {!> docs_src/index/05_rabbit_http_example.py!}
    ```

=== "NATS"
    ```python hl_lines="6 12-14 16-18"
    {!> docs_src/index/05_nats_http_example.py!}
    ```

## Examples

To see more framework usages go to [**examples/**](https://github.com/Lancetnik/Propan/tree/main/examples)

??? tip "Don't forget to stop test container"
    <div class="termy">
    ```console
    $ docker container stop test-mq
    ```
    </div>