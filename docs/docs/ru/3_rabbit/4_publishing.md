# Rabbit Publishing

Для отправки сообщений `RabbitBroker` также использует унифицированный метод `publish`.
Однако, в данном случае в качестве сообщения (помимо `str`, `bytes`, `dict`, `pydatic.BaseModel`) может выступать объект класса `aio_pika.Message` (при необходимости).

```python
from propan.brokers.rabbit import RabbitBroker, RabbitQueue

broker = RabbitBroker()

...
    await broker.publish("Hi!", queue="test", exhcange="test")
```

### Базовые аргументы

Метод `pubslish` принимает следующие аргументы:

* `message`: bytes | str | dict | pydatic.BaseModel | aio_pika.Message = "" - сообщение для отправки
* `exchange`: str | RabbitExchange | None = None - exchange, куда будет отправлено сообщение. Если не указан - используется *default*
* `queue`: str | RabbitQueue = "" - очередь, куда будет отправлено сообщение (т.к. большинство очередей используют свое название в качестве ключа маршрутизации, это человекочитаемый вариант `routing_key`)
* `routing_key`: str = "" - тоже ключ маршрутизации сообщения, если не указан - используется аргумент `queue`

### Параметры сообщения

Подробнее обо всех флагах вы можете прочитать в [документации RabbitMQ](https://www.rabbitmq.com/consumers.html)

* `headers`: dict[str, Any] | None = None - заголовки отправляемого сообщения (используются потребителями)
* `content_type`: str | None = None - content_type отправляемого сообщения. В большинстве случаев выставляется **Propan** автоматически (используется потребителями)
* `content_encoding`: str | None = None - кодировка отправляемого сообщения (используется потребителями)
* `delivery_mode`: aio_pika.abc.DeliveryMode | int | None = 1
    * `1` - NOT_PERSISTENT - не восстанавливать сообщения при перезагрузке *RabbitMQ*
    * `2` - PERSISTENT - восстанавливать сообщения при перезагрузке *RabbitMQ*
* `priority`: int | None = None - приоритет отправляемого сообщения в очереди
* `correlation_id`: str | None = None - id сообщения, который помогает сопоставить исходное сообщение с ответом на него (выставляется **Propan** автоматически)
* `reply_to`: str | None = None - название очереди, куда должнен быть отправлен ответ на сообщение (при использовании блокирующего *RPC* выставляется автоматически)
* `message_id`: str | None = None - идентификатор сообщения (генерируется *RabbitMQ* автоматически)
* `timestamp`: int | float | timedelta | datetime | None - время отправки сообщения (выставляет *RabbitMQ* автоматически)
* `expiration`: int | float | timedelta | datetime | None - время жизни сообщения (в секундах)
* `type`: str | None = None - тип отправляемого сообщения (используется потребителями)
* `user_id`: str | None - идентификатор пользователя *RabbitMQ*, отправившего сообщение
* `app_id`: str | None - идентификатор приложения, отправившего сообщение (используется потребителями)

### Флаги отправки

Аргументы отправки сообщения:

* `mandatory`: bool = True - клиент ожидает подтверждения, что сообщение будет помещено в какую-либо очередь (если очередей нет - вернуть отправителю)
* `immediate`: bool = False - клиент ожидает, что есть потребитель, готовый взять сообщение в работу "прямо сейчас" (если потребителя нет - вернуть отправителю)
* `timeout`: int | float | None = None - время подтверждения отправки от *RabbitMQ*

### RPC аргументы

Также `publish` поддерживает общие аргументы для создания [*RPC* запросов](../../2_getting_started/4_broker/5_rpc/#_3):

* `callback`: bool = False - ожидать ли ответ на сообщение
* `callbakc_timeout`: float | None = 30.0 - таймаут ожидания ответа. В случае `None` - ждет бесконечно
* `raise_timeout`: bool = False
    * `False` - возвращать None в случае таймаута
    * `True` - ошибка `asyncio.TimeoutError` в случае таймаута
