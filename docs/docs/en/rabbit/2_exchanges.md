# EXCHANGES

To declare an `Exchange` with all parameters in `Propan`, a special class `propan.brokers.rabbit.RabbitExchange` is used.

You can use it both when receiving messages and sending them:

```python hl_lines="5 10"
from propan.brokers.rabbit import RabbitBroker, RabbitExchange

broker = RabbitBroker()

@broker.handler("test", exchange=RabbitExchange("test"))
asynchronous definition handler():
      ...

...
      await broker.publish("Hi!", "test", exchange=RabbitExchange("test"))
```

The RabbitExchange constructor takes the following arguments:

* `name`:str - exchange name
* `type`: propan.brokers.rabbit.RabbitExchange = RabbitExchange.DIRECT - exchange routing type
* `durable`: bool = False - if set to True, restore exchange at RabbitMQ restarted
* `auto_delete`: bool = False - if set to True, exchange will be deleted if there are no queues listening to it
* `passive`: bool = False
    * when set to `False`, **Propan** creates an exchange with the required parameters, or check the corresponding parameters of an already existing exchange with the same name.
    * when set to `True`, **Propan** will not create an exchange, but only connect to an existing one. In this case, if the requested exchange does not exist, an error occurred
* `internal`: bool = False - create exchange object at runtime and don't notify RabbitMQ about exchange creation
* `robust`: bool = True - recreate exchange when reconnecting to RabbitMQ
* `timeout`: int | float - response timeout from RabbitMQ
* `arguments`: dict[str, Any] | None = None - exchange custom arguments

And arguments to bind current exchange to another one

* `bind_to`: RabbitExchange | None = None - parent exchange to bind
* `bind_arguments`: dict[str, Any] | None = None - arguments to header exchange routing
* `routing_key`: str = "" - routing key for connecting to exchange
