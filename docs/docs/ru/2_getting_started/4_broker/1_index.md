# Basics

## Разделение зависимостей

**Propan** поддерживает различные брокеры сообщений используя для этого специальные классы

=== "RabbitMQ"
    ```python
    from propan import RabbitBroker
    ```

=== "NATS"
    ```python
    from propan import NatsBroker
    ```

Будьте внимательные! Разные брокеры требуют разных зависимостей. Если вы не установили эти зависимости, импортируемый брокер будет иметь значение `None`.

Для установки **Propan** с необходимыми для вашего брокера зависимостями, выберите один из вариантов установки

=== "RabbitMQ"
    ```bash
    pip install "propan[async-rabbit]"
    ```

=== "NATS"
    ```bash
    pip install "propan[async-nats]"
    ```

## Инициализации брокера

Данные для подключения **Propan Broker** к вашему брокеру сообщений могут быть переданы 2мя способами:

=== "RabbitMQ"
    1. В конструкторе брокера

        ```python
        from propan.brokers.rabbit import RabbitBroker
        broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
        ```

    2. В методе `connect`
    
        ```python
        from propan.brokers.rabbit import RabbitBroker
        broker = RabbitBroker()
        ...
        await broker.connect("amqp://guest:guest@localhost:5672/")
        ```

=== "NATS"
    1. В конструкторе брокера

        ```python
        from propan.brokers.nats import NatsBroker
        broker = NatsBroker("nats://localhost:4222")
        ```

    2. В методе `connect`
    
        ```python
        from propan.brokers.nats import NatsBroker
        broker = NatsBroker()
        ...
        await broker.connect("nats://localhost:4222")
        ```

В простейшем случае вам хватит первого способа передачи данных для подключения - через конструктор.

Однако, в более сложных сценариях: например, при конфигурировании проекта через [переменные окружения](../../2_cli/#_3) вам может понадобиться и второй вариант. Полный пример разобран [здесь](../../6_lifespans/#lifespan)

!!! note
    Параметры, переданные в `connect` имеют приоритет над параметрами, переданными в конструктор. Будьте с этим аккуратны.

    Кроме этого, повторный вызов `connect` не приведет ни к какому эффекту. Поэтому вы можете не опосаться, что вызов `broker.start()`
    (используется внутри `PropanApp` для запуска брокера) вызовет какие-либо ошибки.