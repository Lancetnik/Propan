from propan import PropanApp, KafkaBroker, KafkaRouter

router = KafkaRouter(prefix="user/")

@router.handle("created")
async def handle_user_created_event(user_id: str):
    ...

broker = KafkaBroker()
broker.include_router(router)
app = PropanApp(broker)