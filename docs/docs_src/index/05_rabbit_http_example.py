from contextlib import asynccontextmanager

from fastapi import FastAPI
from propan.brokers.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()
    yield
    await broker.close()

@broker.handle("test")
async def base_handler(body):
    print(body)
