# Rabbit Routing

The advantage of *RabbitMQ* is the ability to configure flexible and complex message routing scenarios.

*RabbitMQ* covers the whole range of routing: from one queue - one consumer, to a queue retrieved from several sources, and the prioritization of messages also works.

!!! note
      For more information about *RabbitMQ* documentation, please visit the [official website](https://www.rabbitmq.com/tutorials/amqp-concepts.html)

At the same time, it supports the ability to successfully process messages, mark them as processed with an error, remove them from the queue (it is also impossible to receive more messages processed, unlike **Kafka**), lock it for the processing duration, and monitor its current status.

Having to keep track of the current status of all messages is a cause of the **RabbitMQ** performance falling. With really large message volumes, **RabbitMQ** starts to degrade. However, if this was a "one-time influx", then as consumers will free it, the "health" of **RabbitMQ** will be restored.

If your scenario is not based on processing millions of messages, and also requires building complex routing logic - **RabbitMQ** you will be right choice.