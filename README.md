<p align="center">
    <a href="https://pypi.org/project/propan" target="_blank">
        <img src="https://img.shields.io/pypi/v/propan?label=pypi%20package" alt="Package version">
    </a>
    <a href="https://pepy.tech/project/propan" target="_blank">
        <img src="https://static.pepy.tech/personalized-badge/propan?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads" alt="downloads"/>
    </a>
    <a href="https://pypi.org/project/propan" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/propan.svg" alt="Supported Python versions">
    </a>
</p>



## Quickstart

Install using `pip`:

```shell
$ pip install "propan[async_rabbit]"
```

### Basic usage

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

### Project template

Project template require `pydantic[dotenv]` installation.

To create project template use:

```shell
$ propan create [projectname]
```

To run created project use:

```shell
# Run rabbimq first
$ docker compose --file [projectname]/docker-compose.yaml up -d

# Run project
$ propan run [projectname].app.serve:app --env=.env --reload
```

Now you can enjoy a new development experience!

## Examples

Too see more use cases go to `examples/`

