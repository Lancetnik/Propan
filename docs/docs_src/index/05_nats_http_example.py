from contextlib import asynccontextmanager

from fastapi import FastAPI
from propan.brokers.nats import NatsBroker

broker = NatsBroker("nats://localhost:4222")

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()
    yield
    await broker.close()

@broker.handle("test")
async def base_handler(body):
    print(body)
