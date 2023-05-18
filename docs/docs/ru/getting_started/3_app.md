# Приложение **PropanApp**

Если вы используете **Propan CLI**, для работы проекта вам необходимо создать экземпляр приложения

```python
from propan import PropanApp
app = PropanApp()
```

!!! tip
    При инициализации `PropanApp` записывает себя в `ContextRepo` под именем `"app"`, поэтому вы всегда можете получить к нему доступ из [контекста](../5_dependency/2_context).

## Использование брокеров

Для того, чтобы `PropanApp` запускал вашего брокера нужно поместить его в объект приложения.

Обычно это делается при объявлении самого приложения

=== "Redis"
    ```python
    {!> docs_src/quickstart/app/1_broker_redis.py!}
    ```

=== "RabbitMQ"
    ```python
    {!> docs_src/quickstart/app/1_broker_rabbit.py!}
    ```

=== "NATS"
    ```python
    {!> docs_src/quickstart/app/1_broker_nats.py!}
    ```

Но, иногда вам может понадобиться инициализировать брокера в другом месте. В таком случае, вы можете использовать метод `app.set_broker`

=== "Redis"
    ```python
    {!> docs_src/quickstart/app/2_set_broker_redis.py!}
    ```

=== "RabbitMQ"
    ```python
    {!> docs_src/quickstart/app/2_set_broker_rabbit.py!}
    ```

=== "NATS"
    ```python
    {!> docs_src/quickstart/app/2_set_broker_nats.py!}
    ```

## Запуск других приложений

Если в `PropanApp` не передавать брокера, все еще будут работать следующие функции:

* Хуки жизненного цикла
* Hotreload кода
* Multiprocessing исполнения

На самом деле, в качестве брокера можно передать экземпляр любого класса, который будет иметь асинхронные методы `start` и `close`

```python
class ABCBroker:
    async def start(self) -> None:
        ...
    
    async def close(self) -> None:
        ...
```

Если ваш код удовлетворяет этому интерфейсу, **PropanApp** может использоваться как удобный инструмент для управления проектом.