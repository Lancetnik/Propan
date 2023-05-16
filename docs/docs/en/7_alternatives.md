# Alternative Frameworks

**Propan** is a pretty young framework. It has a lot of features, but you should know about possible alternatives.
Some of them are focused on other aspects of microservices development, so you can find other features in them that can be helpful in your case.

## [Minos](https://github.com/minos-framework/minos-python){.external-link target="_blank"}

Minos is a framework which helps you create reactive microservices in Python. Internally, it leverages Event Sourcing, CQRS and a message driven architecture to fulfil the commitments of an asynchronous environment.

The `minos` framework is built strongly inspired by the following set of patterns:

* Microservice architecture: Architect an application as a collection of loosely coupled services.
* Decompose by subdomain: Define services corresponding to Domain-Driven Design (DDD) subdomains
* Self-contained Service: Microservices can respond to request without waiting for the response from other service.
* Domain event: A service often needs to publish events when it updates its data. These events might be needed, for example, to update a CQRS view.
* Event Sourcing: Event sourcing persists the state of a business entity such an Order or a Customer as a sequence of state-changing events. Whenever the state of a business entity changes, a new event is appended to the list of events. Since saving an event is a single operation, it is inherently atomic. The application reconstructs an entity's current state by replaying the events.
* Messaging: Services communicating by exchanging messages over messaging channels. (Apache Kafka is used in this case)
* API gateway: Single entry point for all clients. The API gateway proxy/route to the appropriate service.
* Self Registration: Each service instance register on startup and unregister on stop.

## [Kombu](https://docs.celeryq.dev/projects/kombu/en/stable/){.external-link target="_blank"}

**Kombu** is a messaging library for Python.

The aim of **Kombu** is to make messaging in Python as easy as possible by providing an idiomatic high-level interface for the AMQ protocol, and also provide proven and tested solutions to common messaging problems.

* Allows application authors to support several message server solutions by using pluggable transports.
    * AMQP transport using the py-amqp, redis, or `SQS`_ libraries.
    * Virtual transports makes it really easy to add support for non-AMQP transports. There is already built-in support for Redis, Amazon SQS, Azure Storage Queues, Azure Service Bus, ZooKeeper, SoftLayer MQ, MongoDB and Pyro.
    * In-memory transport for unit testing.
* Supports automatic encoding, serialization and compression of message payloads.
* Consistent exception handling across transports.
* The ability to ensure that an operation is performed by gracefully handling connection and channel errors.
* Several annoyances with amqplib has been fixed, like supporting timeouts and the ability to wait for events on more than one channel.
* Projects already using carrot can easily be ported by using a compatibility layer.

## [Nameko](https://nameko.readthedocs.io/en/stable/){.external-link target="_blank"}

**Nameko** is a framework for building microservices in Python.

It comes with built-in support for:

* RPC over AMQP
* Asynchronous events (pub-sub) over AMQP
* Simple HTTP GET and POST
* Websocket RPC and subscriptions (experimental)

Out of the box you can build a service that can respond to RPC messages, dispatch events on certain actions, and listen to events from other services. It could also have HTTP interfaces for clients that can’t speak AMQP, and a websocket interface for, say, Javascript clients.

**Nameko** is also extensible. You can define your own transport mechanisms and service dependencies to mix and match as desired.

**Nameko** strongly encourages the dependency injection pattern, which makes building and testing services clean and simple.
