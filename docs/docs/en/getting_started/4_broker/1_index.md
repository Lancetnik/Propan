---
constructor: In the broker constructor
connect: In the `connect` method
---

# Basics

## Separation of dependencies

**Propan** supports various message brokers using special classes:

{! includes/getting_started/broker/index/imports.md !}

Be careful! Different brokers require different dependencies. If you have not installed these dependencies, the imported broker will have the `None` value.

To install **Propan** with the necessary dependencies for your broker, select one of the installation options:

{! includes/getting_started/broker/index/install.md !}

## Broker Initialization

Data for connecting **Propan Broker** to your message broker can be transmitted in 2 ways:

{% import 'getting_started/broker/index/initialization.md' as includes with context %}
{{ includes }}

In the simplest case, initializing through the constructor is enough for most use cases.

However, if you need more granularity in a complex scenario, for example, when configuring a project via [environment variables](../../2_cli/#environment-management), you may need the second option. The full example is described [here](../../6_lifespans/#lifespan).

!!! note
    The parameters passed to `connect` override the parameters passed to the constructor. Be careful with this.

    In addition, calling `connect` again will have no effect. Therefore, you do not have to worry that `broker.start()` call
    (used inside `PropanApp` to run the broker) will cause any errors.
