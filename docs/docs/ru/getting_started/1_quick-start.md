# Быстрый старт

Для начала, установите фрейморк через `pip`:

=== "Redis"
    <div class="termy">
    ```console
    $ pip install "propan[async-redis]"
    ---> 100%
    ```
    </div>
    !!! tip
        Для работы проекта запустите тестовый контейнер с брокером
        ```bash
        docker run -d --rm -p 6379:6379 --name test-mq redis
        ```

=== "RabbitMQ"
    <div class="termy">
    ```console
    $ pip install "propan[async-rabbit]"
    ---> 100%
    ```
    </div>
    !!! tip
        Для работы проекта запустите тестовый контейнер с брокером
        ```bash
        docker run -d --rm -p 5672:5672 --name test-mq rabbitmq
        ```

=== "Kafka"
    <div class="termy">
    ```console
    $ pip install "propan[async-kafka]"
    ---> 100%
    ```
    </div>
    !!! tip
        Для работы проекта запустите тестовый контейнер с брокером
        ```bash
        docker run -d --rm -p 9092:9092 --name test-mq \
        -e KAFKA_ENABLE_KRAFT=yes \
        -e KAFKA_CFG_NODE_ID=1 \
        -e KAFKA_CFG_PROCESS_ROLES=broker,controller \
        -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
        -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
        -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
        -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://127.0.0.1:9092 \
        -e KAFKA_BROKER_ID=1 \
        -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:9093 \
        -e ALLOW_PLAINTEXT_LISTENER=yes \
        bitnami/kafka
        ```

=== "SQS"
    <div class="termy">
    ```console
    $ pip install "propan[async-sqs]"
    ---> 100%
    ```
    </div>
    !!! tip
        Для работы проекта запустите тестовый контейнер с брокером
        ```bash
        docker run -d --rm -p 9324:9324 --name test-mq softwaremill/elasticmq-native
        ```

=== "NATS"
    <div class="termy">
    ```console
    $ pip install "propan[async-nats]"
    ---> 100%
    ```
    </div>
    !!! tip
        Для работы проекта запустите тестовый контейнер с брокером
        ```bash
        docker run -d --rm -p 4222:4222 --name test-mq nats
        ```

### Базовое использование

Создайте приложение со следующим кодом в `serve.py` файле:

=== "Redis"
    ```python linenums="1" title="serve.py"
    {!> docs_src/quickstart/01_redis_base.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1" title="serve.py"
    {!> docs_src/quickstart/01_rabbit_base.py!}
    ```

=== "Kafka"
    ```python linenums="1" title="serve.py"
    {!> docs_src/quickstart/01_kafka_base.py!}
    ```

=== "SQS"
    ```python linenums="1" title="serve.py"
    {!> docs_src/quickstart/01_sqs_base.py!}
    ```

=== "NATS"
    ```python linenums="1" title="serve.py"
    {!> docs_src/quickstart/01_nats_base.py!}
    ```

И просто запустите его:

<div class="termy">
```console
$ propan run serve:app

2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

---

## Приведение типов

Propan использует `pydantic` для приведения типов входящих аргументов в соответсвии с их аннотацией.

```python linenums="1" hl_lines="5 9"
{!> docs_src/index/02_type_casting.py!}
```

---

## Зависимости

Propan имеет систему управления зависимостями, очень близкую к `pytest fixtures` (но чуть более явную).
Входящие аргументы функции объявляют, какие зависимости нужны, а декоратор - доставляет эти зависимости
из глобального контекста.

По умолчанию, в проекте объявлены следующие зависимости: *app*, *broker*, *context*, *logger* и *message*.
Вы можете в любой момент расширить этот список, добавив свои зависимости.
При попытке доступа к несуществующим зависимостям, вы просто получите *None*.

Также, вы можете вызывать функции в качестве зависимостей (по аналогии с `Fastapi Depends`) и делать некоторые другие трюки.

Подробнее будет [чуть дальше](../5_dependency/1_di-index).

```python linenums="1" hl_lines="11-12"
{!> docs_src/index/03_dependencies.py!}
```

---

## Готовый шаблон

Вы можете сгенерировать готовый к использованию шаблон проекта с помощью **Propan CLI**:

<div class="termy">
```console
$ propan create async [broker] [projectname]
Create Propan project template at: /home/user/projectname
```
</div>

!!! note
    Для запуска, шаблон требует установки `pydantic[dotenv]`

А теперь просто запустите сгенерированный проект

<div class="termy">
```console
### Run rabbimq first
$ docker compose --file [projectname]/docker-compose.yaml up -d [broker]

### Run project
$ propan run [projectname].app.serve:app --env=.env --reload

2023-04-10 23:39:41,140 INFO     - Started reloader process [115536] using WatchFiles
2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

Наслаждайтесь новым опытом разработки!

---

## Использование с HTTP фреймворками

### С любыми фреймворками

Вы можете использовать брокеры Propan без самого Propan приложения.
Просто *запустите* и *остановите* его вместе с вашим HTTP приложением.

=== "Redis"
    ```python linenums="1" hl_lines="5 11-13 16-17"
    {!> docs_src/index/04_redis_http_example.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="5 11-13 16-17"
    {!> docs_src/index/04_rabbit_http_example.py!}
    ```

=== "Kafka"
    ```python linenums="1" hl_lines="5 11-13 16-17"
    {!> docs_src/index/04_kafka_http_example.py!}
    ```

=== "SQS"
    ```python linenums="1" hl_lines="5 11-13 16-17"
    {!> docs_src/index/04_sqs_http_example.py!}
    ```

=== "NATS"
    ```python linenums="1" hl_lines="5 11-13 16-17"
    {!> docs_src/index/04_nats_http_example.py!}
    ```

### С **FastAPI**

Также, **Propan** может использоваться как часть **FastAPI**.

Для этого просто импортируйте нужный вам **PropanRouter** и объявите обработчик сообщений
с помощью декоратора `@event`. Этот декоратор аналогичен декоратору `@handle` у соответсвующих брокеров.

!!! tip
    При использовании таким образом **Propan** не использует собственную систему зависимостей, а интегрируется в **FastAPI**.
    Т.е. вы можете использовать `Depends`, `BackgroundTasks` и прочие инструменты **FastAPI** так, если бы это был обычный HTTP-endpoint.

=== "Redis"
    ```python linenums="1" hl_lines="7 15 19"
    {!> docs_src/index/05_redis_native_fastapi.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="7 15 19"
    {!> docs_src/index/05_rabbit_native_fastapi.py!}
    ```

=== "Kafka"
    ```python linenums="1" hl_lines="7 15 19"
    {!> docs_src/index/05_kafka_native_fastapi.py!}
    ```

=== "SQS"
    ```python linenums="1" hl_lines="7 15 19"
    {!> docs_src/index/05_sqs_native_fastapi.py!}
    ```

=== "NATS"
    ```python linenums="1" hl_lines="7 15 19"
    {!> docs_src/index/05_nats_native_fastapi.py!}
    ```

!!! note
    Больше примеров использования с другими фреймворками вы найдете [здесь](../../integrations/1_integrations-index/)

??? tip "Не забудьте остановить тестовый контейнер"
    ```bash
    docker container stop test-mq
    ```