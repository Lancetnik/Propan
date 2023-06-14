# CHANGELOG

## 2023-06-14 **0.1.3.0** AsyncAPI

Текущее обновление добавляет функционал, над которым я усердно работал последний месяц:
теперь **Propan** может автоматически генерировать и хостить документацию для вашего приложения в
соответствии со спецификацией [**AsyncAPI**](https://www.asyncapi.com/){.external-link target="_blank"}.

Вы можете просто предоставить смежным командам ссылку на страницу с вашей документацией, где они смогут ознакомиться со всеми параметрами используемого сервера, каналов и форматом сообщений, потребляемых вашим сервисом.

![HTML-page](../../assets/img/docs-html-short.png)

Подробнее с этим функционалом вы можете ознакомиться в соответсвующем [разделе документации](getting_started/9_documentation.md).

Также, добавлена возможность определения зависимостей уровня брокера и потребителей:

```python
from propan import RabbitBroker, Depends

broker = RabbitBroker(dependencies=[Depends(...)])

@broker.handler(..., dependencies=[Depends(...)])
async def handler():
    ...
```

## 2023-06-13 **0.1.2.17**

В этом обовлении стоит обобщить несколько изменения и улучшений, выпущенных с предыдущего релиза.

Основное изменение - **Propan** больше не обязывает вас получать сообщение только в виде одного аргумента.
Ваша функция-обработчик может потреблять столько аргументов, сколько необходимо, а также комбинировать их с **pydantic.BaseModel**.

```python
@router.handle(...)
async def handler(a: int, b: float):
...
async def handler(a: Message, b: float, c: str):
```

В **RabbitBroker** добавлены публичные методы для объявления объектов **RabbitMQ**:

```python
broker = RabbitBroker()
...
   await broker.declare_exchange(RabbitExchange("test"))
   await broker.declare_queue(RabbitQueue("test"))
   channel: aio_pika.RobustChannel = broker.channel
```

Для поддержания возможности отправки сообщений и инициализации каналов во все **FastAPI PropanRouters** добавлен `after_startup` хук.

```python
router = RabbitRouter()

@router.after_startup
async def init_whatever(app: FastAPI): ...
```

Кроме этого, улучшено поведение методов `__init__` и `connect` у всех брокеров (теперь параметры `connect` имеют приоритет и переопределяют параметры `__init__` при подключении к брокеру), реализовано корректное исключение при обращении к недоступному для импортирования объекту, исправлено несколько ошибок и произведены другие мелкие внутренние изменения.

## 2023-05-28 **0.1.2.3** SQS Beta

В **Propan** добавлена поддержка *SQS* в качестве брокера сообщений. Данный функционал полностью протестирован.

*SQSBroker* поддерживает:

* доставку сообщений
* тестовый клиент, без необходимости запуска *ElasticMQ* или подключения к облачному *SQS*
* *FastAPI* плагин

*KafkaBroker* на данный момент не поддерживает **RPC** запросы.

Также текущий релиз включает следующие исправления:

* автоматическое восстановления соединения с *Kafka*
* автоматическое восстановления соединения с *Nats*
* *Redis* поддерживает подключение по явным аргументам

## 2023-05-26 **0.1.2.2** NATS Stable

`NatsBroker` полностью протестирован.

Также для **Nats** добавлены:

* Тестовый клиент и тестовые сообщения
* Поддержка **RPC**
* `NatsRouter` для использования с **FastAPI**

## 2023-05-23 **0.1.2.0** Kafka

В **Propan** добавлена поддержка *Kafka* в качестве брокера сообщений. Данный функционал полностью протестирован.

*KafkaBroker* поддерживает:

* доставку сообщений
* тестовый клиент, без необходимости запуска *Kafka*
* В качестве плагина *FastAPI*

*KafkaBroker* на данный момент не поддерживает **RPC** запросы.

## 2023-05-18 **0.1.1.0** REDIS

В **Propan** добавлена поддержка *Redis Pub/Sub* в качестве брокера сообщений. Данный функционал полностью протестирован и описан в документации.

*RedisBroker* поддерживает:

* доставку сообщений по ключу или паттерну
* тестовый клиент, без необходимости запуска *Redis*
* **RPC** запросы поверх *Redis Pub/Sub*
* В качестве плагина *FastAPI*

Также, **Propan CLI** теперь позволяет генерировать шаблоны проектов для использования с различными брокерами сообщений

```bash
propan create async [broker] [APPNAME]
```

## 2023-05-15 **0.1.0.0** STABLE

Стабильный и полностью задокументированный релиз **Propan**!

С текущего релиза больше не предвидется изменений, нарушающих обратную совместимость - используйте фреймворк смело!

На данный момент поддерживаются, протестированы и описаны в документации все варианты взаимодействия с *RabbitMQ*.
В скором времени ожидайте поддержку *Redis* (находится в тестировании сейчас), *Kafka* (находится в разработке) и полную поддержку *Nats* (также в разработке).

## 2023-05-01 **0.0.9.4**

Отличные новости! Теперь **Propan** можно использовать как полноценную часть **FastAPI**!

```python
from fastapi import FastAPI
from propan.fastapi import RabbitRouter

router = RabbitRouter("amqp://guest:guest@localhost:5672")

app = FastAPI(lifespan=router.lifespan_context)

@router.event("test")
async def hello(m: dict) -> dict:
    return { "response": "Hello, Propan!" }

app.include_router(router)
```

Полный пример вы можете найти в [документации](../integrations/2_fastapi-plugin)

Также, добавлена возможность [тестировать](../getting_started/7_testing) свое приложение без запуска внешних зависимостей в виде брокера (пока только для RabbitMQ)!

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

Также добавлена поддержка [RPC over MQ](../getting_started/4_broker/5_rpc) (пока только для RabbitMQ): `return` вашей функции-обработчика будет отправлен в ответ на сообщение, если ответ ожидается.

<h3>Breaking changes:</h3>

* метод брокеров `publish_message` был переименован в `publish`
* удален аргумент `declare` в `RabbitQueue` и `RabbitExchange` - теперь необходимо использовать `passive`

## 2023-04-18 **0.0.9**

Релиз приурочен к выходу в свет другой библиотеки: [fast-depends](https://lancetnik.github.io/FastDepends/).
Теперь **Propan** используется ее в качестве системы управления зависимостями. `Context` также переосмыслен - теперь
это наследник *fast-depends CustomField*.

<h3>Особенности сборки:</h3>

* Вложенность `Depends`
* Более гибкое поведение `Context`
* Полностью протестированная и стабильная система управления зависимостями
* Добавлен модуль `propan.annotation` для быстрого доступа к уже существующим объектам контекста

<h3>Breaking changes:</h3>

* `@use_context` был удален. Используйте `@apply_types` для внедрения `Context`
* `Alias` был перемещен как часть `Context`
* Доступ к объектам контекста больше нельзя получить просто объявив аргумент функции

Теперь нужно использовать следующий код:

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

Привет! Поздравляю всех и, особенно, себя с первым стабильным релизом *Propan*!

</h3>Особенности сборки</h3>
</h4>Стабильныe</h4>

* async RabbitMQ broker
* инъекция зависимостей
* преобразование типов
* инструмент CLI

<h4>Экспериментальные</h4>
В релиз добавлена первая реализация поддержки *NATS* (без использования Jetstream).

<h4>Следующие шаги</h4>

* Полная поддержка NATS
* Синхронная версия брокеров и приложения
* Разработка инструментов тестирования
