# CHANGELOG

## 2023-05-01 **0.0.9.4**

Отличные новости! Теперь **Propan** можно использовать как полноценную часть **FastAPI**!

```python
from fastapi import FastAPI
from propan.fastapi import RabbitRouter

app = FastAPI()

router = RabbitRouter("amqp://guest:guest@localhost:5672")

@router.event("test")
async def hello(m: dict) -> dict:
    return { "response": "Hello, Propan!" }

app.include_router(router)
```

Полный пример вы можете найти в [документации](../5_integrations/2_fastapi-plugin)

Также, добавлена возможность [тестировать](../2_getting_started/7_testing) свое приложение без запуска внешних зависимостей в виде брокера (пока только для RabbitMQ)!

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

Также добавлена поддержка [RPC over MQ](../2_getting_started/4_broker/5_rpc) (пока только для RabbitMQ): `return` вашей функции-обработчика будет отправлен в ответ на сообщение, если ответ ожидается.

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
