# Basics

## Separation of dependencies

**Propan** supports various message brokers using special classes

=== "RabbitMQ"
    ```python
    from propan import RabbitBroker
    ```

=== "NATS"
    ```python
    from propan import NatsBroker
    ```

Be careful! Different brokers require different dependencies. If you have not install these dependencies, the imported broker will have the `None` value.

To install **Propan** with the necessary dependencies for your broker, select one of the installation options

=== "RabbitMQ"
    ```bash
    pip install "propan[async-rabbit]"
    ```

=== "NATS"
    ```bash
    pip install "propan[async-nats]"
    ```

## Broker Initialization

Data for connecting **Propan Broker** to your message broker can be transmitted in 2 ways:

=== "RabbitMQ"
    1. In the broker constructor
        ```python
        from propan.brokers.rabbit import RabbitBroker
        broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
        ```

    2. In the `connect` method
        ```python
        from propan.brokers.rabbit import RabbitBroker
        broker = RabbitBroker()
        ...
        await broker.connect("amqp://guest:guest@localhost:5672/")
        ```

=== "NATS"
    1. In the broker constructor
        ```python
        from propan.brokers.nats import NatsBroker
        broker = NatsBroker("nats://localhost:4222")
        ```

    2. In the `connect` method
        ```python
        from propan.brokers.nats import NatsBroker
        broker = NatsBroker()
        ...
        await broker.connect("nats://localhost:4222")
        ```

In the simplest cases, the first method of data transmission for connection is enough for you - through the constructor.

However, in more complex scenarios: for example, when configuring a project via [environment variables](../../2_cli/#environment-management), you may need the second option. The full example is described [here](../../6_lifespans/#lifespan)

!!! note
    The parameters passed to `connect` overrides the parameters passed to the constructor. Be careful with this.

    In addition, calling `connect` again has no effect. Therefore, you may not worry that `broker.start()` call
    (used inside 'PropanApp` to run the broker) will cause any errors.