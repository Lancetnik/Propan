# LOGGING

**Propan** uses 2 previously configured loggers:

* `propan` - using by PropanApp
* `propan.access` - using by broker

## Logging requests

To log requests, it is strongly recommended to use the `access_logger` of your broker, since it is available from the [Context](../../5_dependency/2_context) of your application.

```python
from propan import RabbitBroker
from propan.annotations import Logger

broker = RabbitBroker()

@broker.handle("test")
async def func(logger: Logger):
logger.info("message received")
```

This approach has several advantages:

* the logger already contains the request context: message ID, broker-based params
* by replacing the `logger` at broker initializing, you will automatically replace all loggers inside your functions

## Logging levels

If you use the **Propan CLI**, you can change the current logging level of the entire application directly from the command line.

The `--log-level` flag sets the current logging level for both a broker and a PropanApp. This way you can configure the levels of not only default loggers, but also your own, if you use them inside **Propan**

<div class="termy">
```console
$ propan run serve:app --log-level debug
```
</div>

If you want to completely disable the default logging of `Propan`, you can set `logger=None'

```python
from propan import PropanApp, RabbitBroker

broker = RabbitBroker(logger=None) # disables broker logs
app = PropanApp(broker, logger=None) # disables application logs
```

!!! warning
    Be careful: the `logger` that you get from the context will also have the value `None' if you turn off the broker logging

If you don't want to lose access to the `logger' inside your context, but want to get rid of the default logs **Propan**, you can lower the level of logs that the broker publishes itself.

```python
import logging
from propan import PropanApp, RabbitBroker

# sets the broker logs to the DEBUG level
broker = RabbitBroker(log_level=logging.DEBUG)
```

## Formatting logs

If you are not satisfied with the current format of your application logs, you can change it directly in your broker's constructor

```python
from propan import PropanApp, RabbitBroker
broker = RabbitBroker(log_fmt="%(asctime)s %(levelname)s - %(message)s")
```

## Using your own loggers

Since **Propan** works with the standard `logging.Logger` object, you can initiate an application and a broker
using your own logger

```python
import logging
from propan import PropanApp, RabbitBroker

logger = logging.getLogger("my_logger")

broker = RabbitBroker(logger=logger)
app = PropanApp(broker, logger=logger)
```

Doing so, you will lose information about the context of the current request. However, you can get it directly from the context anywhere in your code:

```python
from propan import context
log_context: dict[str, str] = context.get_local("log_context")
```

## Logger access

If you want to override default loggers behavior, you can access them directly via `logging`:

```python
import logging
logger = logging.getLogger("propan")
access_logger = logging.getLogger("propan.access")
```

Or by importing them from **Propan**

```python
from propan.log import access_logger, logger
```
