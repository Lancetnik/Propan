# Basics

## Разделение зависимостей

**Propan** поддерживает различные брокеры сообщений используя для этого специальные классы

=== "RabbitMQ"
    ```python
    from propan.brokers.rabbit import RabbitBroker
    ```

=== "NATS"
    ```python
    from propan.brokers.nats import NatsBroker
    ```

Обратите внимание, что различные брокеры импортируются из разных модулей `propan.broker.*`.
Это сделано для того, чтобы работая с одним из брокеров, вы не могли по ошибке импортировать участки кода другого.
Так как каждый из брокеров имеет уникальные зависимости, разделение импортов таким образом позволяет избежать необходимости ставить
все зависимости различных брокеров.

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

Однако, в более сложных сценариях: например, при конфигурировании проекта через [переменные окружения](/Propan/2_getting_started/2_cli/#_3) вам может понадобиться и второй вариант. Полный пример разобран [здесь](/Propan/2_getting_started/6_lifespans/#lifespan)

!!! note
    Параметры, переданные в `connect` имеют приоритет над параметрами, переданными в конструктор. Будьте с этим аккуратны.