# NATS JetStream

The default **NATS** usage is suitable for scenarios where:

* `publisher` and `consumer` are always online;
* a system tolerate to the messages loss.

If you need stricter restrictions, like:

* an availability of a message processing confirmation mechanism (`ack`/`nack');
* message persistence (will accumulate in the queue when `consumer` is offline).

You should use the **NATS JetStream** extension.

In fact, the **JetStream** extension is the same **NATS** with the addition a persistent layer above the file system. Therefore, all interfaces for publishing and consuming messages are similar to the refular **NATS** usage.

However, the **JetStream** layer has many possibilities for configuration: from the deleting old messages policy to the maximum stored messages number limit. You can find out more about all **JetStream** features in the official [documentation](https://docs.nats.io/using-nats/developer/develop_jetstream ){.external-link target="_blank"}.

!!! tip ""
    If you have worked with other message brokers, then you should know that the logic of **JS** is closer to **Kafka** than to **RabbitMQ**: messages after confirmation are not deleted from the queue, but remain there until the queue is full and it will start deleting old messages (or in accordance with other logic that you can configure yourself).

    When connecting a `consumer` (and, especially, when reconnecting), you must determine for yourself, according to what logic it will consume messages: from the subject beginning, starting with some message, starting from some time, only new ones, etc. Don't be surprised if a connection is restored, your `consumer` starts to process all messages received earlier again - you haven't defined the rule.

Also **NATS JetStream** has built-in `key-value` (close to **Redis**) and `object` (close to **Minio**) storages, which, in addition to interface *put/get* have the ability to subscribe to events, which can be extremely useful in vary scenarios.

**Propan** does not provide access to this functionality directly, but it is covered by the [nats-py] library used({{urls.nats_py }}){target="_blank"}. You can access the **JS** object from the application context:

```python linenums="1" hl_lines="2 8"
{!> docs_src/nats/js.py !}
```
