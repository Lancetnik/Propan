"""
Propan use dependencies management policy close to `pytest fixtures`.
You can specify in functions argument parameters which dependencies
you would to use. And framework passes them from the global Context object.

Default context fields are: app, broker, context (itself), logger and message.
If you call not existed field, raises "pydantic.error_wrappers.ValidationError" value.
"""
from propan import Context, PropanApp, RabbitBroker
from propan.annotations import App, ContextRepo, Logger
from propan.annotations import RabbitBroker as Rabbit
from propan.annotations import RabbitMessage

rabbit_broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(rabbit_broker)


@rabbit_broker.handle("test")
async def base_handler(
    body: dict,
    app: App,
    broker: Rabbit,
    context: ContextRepo,
    logger: Logger,
    message: RabbitMessage,
    not_found_field=Context(default=None),
):
    assert not_found_field is None
    assert broker is rabbit_broker
