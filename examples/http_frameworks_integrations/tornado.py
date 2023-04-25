"""
You can use Propan MQBrokers without PropanApp
Just start and stop them whenever you want
"""
import asyncio

import tornado.web

from propan import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")


@broker.handle("test")
async def base_handler(body):
    print(body)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),
        ]
    )


async def main():
    app = make_app()
    app.listen(8888)

    await broker.start()
    try:
        await asyncio.Event().wait()
    finally:
        await broker.close()


if __name__ == "__main__":
    asyncio.run(main())
