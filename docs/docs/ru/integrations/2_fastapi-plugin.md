# **FastAPI** Plugin

### Прием сообщений

**Propan** может использоваться как полноценная часть **FastAPI**.

Для этого просто импортируйте нужный вам **PropanRouter** и объявите обработчик сообщений
с помощью декоратора `@event`. Этот декоратор аналогичен декоратору `@handle` у соответсвующих брокеров.

!!! tip
    При использовании таким образом **Propan** не использует собственную систему зависимостей, а интегрируется в **FastAPI**.
    Т.е. вы можете использовать `Depends`, `BackgroundTasks` и прочие инструменты **FastAPI** так, если бы это был обычный HTTP-endpoint.

    Обратите внимание, что в коде ниже используется `fastapi.Depends`, а не `propan.Depends`.

=== "Redis"
    ```python linenums="1" hl_lines="1 3 7 15 19 23"
    {!> docs_src/integrations/fastapi_plugin_redis.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="1 3 7 15 19 23"
    {!> docs_src/integrations/fastapi_plugin_rabbit.py!}
    ```

При обработке сообщения из брокера все тело сообщения помещается одновременно и в `body`, и в `path` параметры запроса: вы можете достать получить к ним доступ любым удобным для вас способом. Заголовок сообщения помещается в `headers`.

Также этот роутер может полноценно использоваться как `HttpRouter` (наследником которого он и является). Поэтому вы можете
объявлять с его помощью любые `get`, `post`, `put` и прочие HTTP методы. Как например, это сделано в строке **19**.

### Отправка сообщений

Внутри каждого роутера есть соответсвующий брокер. Вы можете легко получить к нему доступ, если вам необходимо отправить сообщение в MQ.

=== "Redis"
    ```python linenums="1" hl_lines="6 10"
    {!> docs_src/integrations/fastapi_plugin_redis_send.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="6 10"
    {!> docs_src/integrations/fastapi_plugin_rabbit_send.py!}
    ```

Вы можете оформить доступ к брокеру в виде `Depends`, если хотите использовать его в разных частях вашей программы.

=== "Redis"
    ```python linenums="1" hl_lines="8 14-15"
    {!> docs_src/integrations/fastapi_plugin_redis_depends.py!}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="8 14-15"
    {!> docs_src/integrations/fastapi_plugin_rabbit_depends.py!}
    ```
