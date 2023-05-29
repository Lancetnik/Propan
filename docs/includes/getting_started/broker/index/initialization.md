=== "Redis"
    1. {{ constructor }}

        ```python
        from propan import RedisBroker
        broker = RedisBroker("redis://localhost:6379/")
        ```

    2. {{ connect }}
        ```python

        from propan import RedisBroker
        broker = RedisBroker()
        ...
        await broker.connect("redis://localhost:6379/")
        ```

=== "RabbitMQ"
    1. {{ constructor }}

        ```python
        from propan import RabbitBroker
        broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
        ```

    2. {{ connect }}

        ```python
        from propan import RabbitBroker
        broker = RabbitBroker()
        ...
        await broker.connect("amqp://guest:guest@localhost:5672/")
        ```

=== "Kafka"
    1. {{ constructor }}

        ```python
        from propan import KafkaBroker
        broker = KafkaBroker("localhost:9092")
        ```

    2. {{ connect }}

        ```python
        from propan import KafkaBroker
        broker = KafkaBroker()
        ...
        await broker.connect("localhost:9092")
        ```

=== "SQS"
    1. {{ constructor }}

        ```python
        from propan import SQSBroker
        broker = SQSBroker("http://localhost:9324")
        ```

    2. {{ connect }}

        ```python
        from propan import SQSBroker
        broker = SQSBroker()
        ...
        await broker.connect("http://localhost:9324")
        ```

=== "NATS"
    1. {{ constructor }}

        ```python
        from propan import NatsBroker
        broker = NatsBroker("nats://localhost:4222")
        ```

    2. {{ connect }}

        ```python
        from propan import NatsBroker
        broker = NatsBroker()
        ...
        await broker.connect("nats://localhost:4222")
        ```
