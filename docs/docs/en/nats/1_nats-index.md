# NATS

## Advantages and disadvantages

**NATS** is an easy-to-use, high-performance message broker written in *Golang*. If your application does not require complex routing logic, should cope with high load, scale and do not require large hardware costs, *NATS* will be an excellent choice for you.

!!! note
    More information about *NATS* can be found on the [official website](https://nats.io ){.external-link target="_blank"}

However, *NATS* has disadvantages that you should be aware of:

* Messages are not persistent. If the message is published while your consumer is disconnected, it will be lost.
* There are no complex routing mechanisms.
* There are no mechanisms for confirming receipt and processing of messages from the consumer.

These shortcomings are corrected by using the persistent level - *JetStream*. If you need strict guarantees for the delivery and processing of messages to the small detriment of the speed and resources consumed, you can use *NatsJS*.

## Routing rules

*NATS* does not have the ability to configure complex routing rules. The only entity in *NATS* is `subject`, which can be subscribed to either directly by name or by regular expression pattern.

Both examples are discussed [a little further](../3_examples/1_direct).

In order to support the ability to scale consumers horizontally, *NATS* supports the `queue group` functionality:
a message sent to `subject` will be processed by a random consumer from the `queue group` subscribed to this `subject`.
This approach allows you to increase the processing speed of `subject` by *N* times when starting *N* consumers with one group.
