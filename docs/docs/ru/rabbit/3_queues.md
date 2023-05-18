# QUEUES

Для объявления `Queue` со всеми параметрами в `Propan` используется специальный класс `propan.brokers.rabbit.RabbitQueue`.

Вы можете использовать его как при получании сообщений, так и при их отправке:

```python hl_lines="5 10"
from propan.brokers.rabbit import RabbitBroker, RabbitQueue

broker = RabbitBroker()

@broker.handler(RabbitQueue("test"))
async def handler():
    ...

...
    await broker.publish("Hi!", RabbitQueue("test"))
```

Конструктор `RabbitQueue` принимает следующие аргументы:

* `name`: str - название очереди
* `durable`: bool = False - при установке в True, информация об очереди будет хранится в файловой системе и восстанавливаться при перезагрузке RabbitMQ
* `auto_delete`: bool = False - при установке в True, очередь будет удалена при отключении клиента от RabbitMQ
* `exclusive`: bool = False - к этой очереди возможно подключиться только в рамках текущего соединения. Такая очередь также будет удалена при отключении от RabbitMQ.
* `passive`: bool = False
    * при установке в `False`, **Propan** попытается создать очередь с требуемыми параметрами, либо провалидирует соответсвие этих параметров уже существующей очереди с таким именем.
    * при установке в `True`, **Propan** не будет создавать очередь, а только подключится к существующей. При этом, если запрашиваемая очередь не существует, возникнет ошибка
* `robust`: bool = True - пересоздавать очередь при переподключении к RabbitMQ
* `timeout`: int | float - время ожидания ответа от RabbitMQ
* `arguments`: dict[str, Any] | None = None - кастомные аргументы очереди
  
Параметры подключения очереди к exchange также передаются в ее конструкторе:

* `routing_key`: str - ключ маршрутизации для подключения к exchange. Если не указан - используется агрумент `name`
* `bind_arguments`: dict[str, Any] | None = None - аргументы подключения (используются для header exchange маршрутизации)
