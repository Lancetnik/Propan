# NATS Publishing

Для отправки сообщений `NatsBroker` использует унифицированный метод `publish`.

```python
import asyncio
from propan import NatsBroker

async def pub():
    async with NatsBroker() as broker:
        await broker.publish("Hi!", subject="test")

asyncio.run(pub())
```

## Базовые аргументы

Метод `publish` принимает следующие аргументы:

* `message`: bytes | str | dict | Sequence[Any] | pydantic.BaseModel - сообщение для отправки
* `subject`: str - *subject*, куда будет отправлено сообщение.

## Параметры сообщения

* `headers`: dict[str, Any] | None = None - заголовки отправляемого сообщения (используются потребителями)

## RPC аргументы

Также `publish` поддерживает общие аргументы для создания [*RPC* запросов](../../getting_started/4_broker/5_rpc/#_3):

* `reply_to`: str = "" - в какой *channel* отправить ответ (используется для асинхронных RPC запросов)
* `callback`: bool = False - ожидать ли ответ на сообщение
* `callback_timeout`: float | None = 30.0 - таймаут ожидания ответа. В случае `None` - ждет бесконечно
* `raise_timeout`: bool = False
    * `False` - возвращать None в случае таймаута
    * `True` - ошибка `TimeoutError` в случае таймаута
