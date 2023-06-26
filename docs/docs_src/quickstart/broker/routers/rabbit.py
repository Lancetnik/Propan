from propan import PropanApp, RabbitBroker, RabbitRouter

router = RabbitRouter(prefix="user/")

@router.handle("created")
async def handle_user_created_event(user_id: str):
    ...

broker = RabbitBroker()
broker.include_router(router)
app = PropanApp(broker)