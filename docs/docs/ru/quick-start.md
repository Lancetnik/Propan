# Быстрый старт

Для начала, установите фрейморк через `pip`:

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

=== "RabbitMQ"
    ```python
    {!> docs_src/index/01_rabbit_base.py!}
    ```

=== "NATS"
    ```python
    {!> docs_src/index/01_nats_base.py!}
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

=== "RabbitMQ"
    ```python hl_lines="12"
    {!> docs_src/index/02_rabbit_type_casting.py!}
    ```

=== "NATS"
    ```python hl_lines="12"
    {!> docs_src/index/02_nats_type_casting.py!}
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

Подробнее будет [чуть дальше](https://lancetnik.github.io/Propan/dependency/di-index/).

=== "RabbitMQ"
    ```python hl_lines="12-17"
    {!> docs_src/index/03_rabbit_dependencies.py!}
    ```

=== "NATS"
    ```python hl_lines="12-17"
    {!> docs_src/index/03_nats_dependencies.py!}
    ```

---

## Готовый шаблон

Вы можете сгенерировать готовый к использованию шаблон проекта с помощью **propan cli**:

<div class="termy">
```console
$ propan create [projectname]
Create Propan project template at: /home/user/projectname
```
</div>

!!! note
    Для запуска, шаблон требует установки `pydantic[dotenv]`

А теперь просто запустите сгенерированный проект

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

Наслаждайтесь новым опытом разработки!

---

## Использование с HTTP фреймворками

Вы можете использовать брокеры Propan без самого Propan приложения.
Просто *запустите* и *остановите* его вместе с вашим HTTP приложением.

=== "RabbitMQ"
    ```python hl_lines="6 12-14 16-18"
    {!> docs_src/index/05_rabbit_http_example.py!}
    ```

=== "NATS"
    ```python hl_lines="6 12-14 16-18"
    {!> docs_src/index/05_nats_http_example.py!}
    ```

!!! note
    Больше примеров использования с другими фреймворками вы найдете [здесь](https://lancetnik.github.io/Propan/integrations/integrations-index/)

??? tip "Не забудьте остановить тестовый контейнер"
    ```bash
    $ docker container stop test-mq
    ```