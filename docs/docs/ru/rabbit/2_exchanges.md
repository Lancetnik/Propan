# EXCHANGES

Для объявления `Exchange` со всеми параметрами в `Propan` используется специальный класс `propan.brokers.rabbit.RabbitExchange`.

Вы можете использовать его как при получании сообщений, так и при их отправке:

```python hl_lines="5 10"
from propan.brokers.rabbit import RabbitBroker, RabbitExchange

broker = RabbitBroker()

@broker.handler("test", exchange=RabbitExchange("test"))
async def handler():
    ...

...
    await broker.publish("Hi!", "test", exchange=RabbitExchange("test"))
```

Конструктор `RabbitExchange` принимает следующие аргументы:

* `name`: str - название exchange
* `type`: propan.brokers.rabbit.RabbitExchange = RabbitExchange.DIRECT - тип вашего exchange
* `durable`: bool = False - при установке в True, информация об exchange будет хранится в файловой системе и восстанавливаться при перезагрузке RabbitMQ
* `auto_delete`: bool = False - при установке в True, exchange будет удален при отсутсвии очередей, которые его слушают
* `passive`: bool = False
    * при установке в `False`, **Propan** попытается создать exchange с требуемыми параметрами, либо провалидирует соответсвие этих параметров уже существующему exchange с таким именем.
    * при установке в `True`, **Propan** не будет создавать exchange, а только подключится к существующему. При этом, если запрашиваемого exchange не существует, возникнет ошибка
* `internal`: bool = False - создать объект exchange в рантайме и не уведомлять RabbitMQ о создании exchange
* `robust`: bool = True - пересоздавать exchange при переподключении к RabbitMQ
* `timeout`: int | float - время ожидания ответа от RabbitMQ
* `arguments`: dict[str, Any] | None = None - кастомные аргументы для exchange

А также аргументы для прикрепления создаваемого exchange к другому

* `bind_to`: RabbitExchange | None = None - родительский exchange, на который нужно подписаться
* `bind_arguments`: dict[str, Any] | None = None - аргументы подключения (используются для header exchange маршрутизации)
* `routing_key`: str = "" - ключ маршрутизации при подписке на родительский exchange