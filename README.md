<p align="center">
    <a href="https://pypi.org/project/propan" target="_blank">
        <img src="https://img.shields.io/pypi/v/propan?color=%2334D058&label=pypi%20package" alt="Package version">
    </a>
    <a href="https://pypi.org/project/propan" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/propan.svg?color=%2334D058" alt="Supported Python versions">
    </a>
</p>



## Quickstart

Install using `pip`:

```shell
$ pip install "propan[async_rabbit]"
```

Create an application, in `example.py`:

```python
from propan.app import PropanApp
from propan.brokers import RabbitBroker


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@broker.handle("test")
async def base_handler(body: dict):
    '''Handle all default exchange messages with `test` routing key'''
    print(body)
```

Run the application:

```shell
$ propan run example:app --reload
```

Too see more use cases go to `examples/`
