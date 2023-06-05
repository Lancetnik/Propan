# Redis Pub/Sub

## Advantages and disadvantages

Most likely, your project already uses *Redis*. If you want to use asynchronous messaging, but do not want
to include a new heavy dependency (*Kafka*, *RabbitMQ*, *Nats*, etc.) to your infrastructure, you should use it as a message broker.

*Redis* works fast, does not degrade with a large number of messages, and most importantly - you already have it!

!!! note
    More information about *Redis Pub/Sub* can be found at [official website](https://redis.io/docs/manual/pubsub/#messages-matching-both-a-pattern-and-a-channel-subscription){.external- link target="_blank"}

However, *Redis* as a message broker has some important disadvantages:

* Messages are not persistent. If the message is published while your consumer is disconnected, it will be lost.
* There is no possibility of horizontal scaling of consumers.
* There are no complex routing mechanisms.
* There are no mechanisms for confirming receipt and processing of messages from the consumer.
* Messages are represented by raw bytes without meta-information.

Not all of these features are necessary for your project, but you should keep them in mind when choosing *Redis* as a message broker.

In any case, since the **Propan** application code is weakly dependent on the message broker used, you can build a prototype of your system based on *Redis* and if necessary quickly adapt it to use another broker.

Also, *Redis 5.0+* contains the *Streams* mechanism, which can also serve as a message broker and covers the main disadvantages of *Redis Pub/Sub*: message persistence and consumer scaling.

## Routing rules

*Redis* cannot configure complex routing rules. The only entity in *Redis Pub/Sub* is `channel`, which can be subscribed to either directly by name or by regular expression pattern.

Both examples are described [a little further](../3_examples/1_direct).

## Features **Propan**

Since *Redis* uses just a set of bytes without headers and other meta information as a message, **Propan** uses encoded *json* with the following structure as a message:

```json
{
"data": "",
"headers": {},
"reply_to": ""
}
```

This is necessary for the correct recognition of the *content-type* of the incoming message (necessary for valid decoding) and support for **RPC** requests.

If **Propan** receives a message sent using another library or framework (or just a message in a different format),
the entire body of this message will be perceived as the `data` field of the received message, and the `content-type` will be recognized automatically.

At the same time, **RPC** requests will not work, since there is no `reply_to` field in the incoming message.
