# Отправка сообщений

В **Propan** для отправки сообщений используется унифицированный метод

```python
await broker.pubslih(message, ...)
```

Этот метод, независимо от брокера, принимает первым аргументом `message`. Однако, остальные аргументы являются
специфичными для разных брокеров.

Ознакомиться со всеми особенностями, специфичными для вашего брокеры, вы можете здесь:

* [Redis](../../../redis/2_publishing)
* [RabbitBroker](../../../rabbit/4_publishing)
* [NatsBroker](../../../nats/3_publishing)

## Допустимые типы для отправки

| Тип                  | Заголовок при отправке      | Способ приведения к bytes    |
| -------------------- | --------------------------- | ---------------------------- |
| `dict`               | application/json            | json.dumps(message).encode() |
| `Sequence`           | application/json            | json.dumps(message).encode() |
| `pydantic.BaseModel` | application/json            | message.json().encode()      |
| `str`                | text/plain                  | message.encode()             |
| `bytes`              |                             | message                      |

Также, некоторые брокеры поддерживают отправку специальных типов, которые описаны в соотвествующем разделе документации вашего брокера.

## Инициализация брокера перед отправкой

Для того, чтобы отправить сообщение в очерендь, необходимо сначала подключиться к ней.

Если вы находитесь внутри запущенного **Propan** приложения, вам не нужно ничего делать: брокер уже запущен.
Просто получите к нему доступ и отправьте сообщение.

=== "Redis"
    ```python linenums="1" hl_lines="8"
    {!> docs_src/quickstart/broker/publishing/1_redis_inside_propan.py !}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="8"
    {!> docs_src/quickstart/broker/publishing/1_rabbit_inside_propan.py !}
    ```

=== "NATS"
    ```python linenums="1" hl_lines="8"
    {!> docs_src/quickstart/broker/publishing/1_nats_inside_propan.py !}
    ```

Если же вы используете **Propan** только для отправки асинхронных сообщений в рамках другого фреймворка, вы можете использовать
брокер в качестве контекстного менеджера для отправки.

=== "Redis"
    ```python
    {!> docs_src/quickstart/broker/publishing/2_redis_context.py !}
    ```

=== "RabbitMQ"
    ```python
    {!> docs_src/quickstart/broker/publishing/2_rabbit_context.py !}
    ```

=== "NATS"
    ```python
    {!> docs_src/quickstart/broker/publishing/2_nats_context.py !}
    ```

!!! tip
    В рамках этого контекста вы можете отправлять неограниченное число сообщений, а также синхронно ожидать ответ на них.
    Однако, инициализировать `handle`'ы в рамках этого контекста нельзя: они завершат свое выполнение вместе с контекстом.

    Подробнее это будет разобрано в следующем разделе.
