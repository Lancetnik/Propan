from logging import Logger

import nats.aio.msg
from propan import PropanApp, Context
from propan.brokers.nats import NatsBroker

gl_broker = NatsBroker("nats://localhost:4222")
app = PropanApp(gl_broker)

@gl_broker.handle("test")
async def base_handler(body: dict,
                       app: PropanApp,
                       broker: NatsBroker,
                       context: Context,
                       logger: Logger,
                       message: nats.aio.msg.Msg,
                       not_existed_field):
    assert broker is gl_broker
    assert not_existed_field is None