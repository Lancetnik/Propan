# QUEUES

To declare a `Queue` with all parameters in `Propan`, a special class `propan.brokers.rabbit.RabbitQueue` is used.

You can use it both when receiving messages and sending them:

```python hl_lines="5 10"
from propan.brokers.rabbit import RabbitBroker, RabbitQueue

broker = RabbitBroker()

@broker.handler(RabbitQueue("test"))
asynchronous definition handler():
      ...

...
      await broker.publish("Hi!", RabbitQueue("test"))
```

The `RabbitQueue` constructor takes the following arguments:

* `name`: str - queue name
* `durable`: bool = False - if set to True, restore queue at RabbitMQ restarted
* `auto_delete`: bool = False - if set to True, delete queue with RabbitMQ disconnected
* `exclusive`: bool = False - this queue can only be connected within the current connection. Such a queue will also be deleted when disconnected from RabbitMQ.
* `passive`: bool = False
     * when set to `False`, **Propan** will attempt to create a queue with the required parameters, or check those parameters to match an already existing queue with the same name.
     * when set to `True`, **Propan** will not create a queue, but only connect to an existing one. In this case, if the requested queue does not exist, an error will occur.
* `robust`: bool = True - recreate the queue when reconnecting to RabbitMQ
* `timeout`: int | float - response timeout from RabbitMQ
* `arguments`: dict[str, Any] | None = None - custom queue arguments
  
The parameters for connecting the queue to exchange are also passed in its constructor:

* `routing_key`: str - routing key for connecting to exchange. If not specified, the `name` argument is used
* `bind_arguments`: dict[str, Any] | None = None - arguments to header exchange routing