from fastapi import FastAPI
from propan.brokers.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = FastAPI()

@broker.handle("test")
async def base_handler(body):
    print(body)

@app.on_event("startup")
async def start_broker():
    await broker.start()

@app.on_event("shutdown")
async def stop_broker():
    await broker.close()