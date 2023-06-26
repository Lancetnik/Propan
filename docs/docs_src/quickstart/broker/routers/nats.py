from propan import PropanApp, NatsBroker, NatsRouter

router = NatsRouter(prefix="user/")

@router.handle("created")
async def handle_user_created_event(user_id: str):
    ...

broker = NatsBroker()
broker.include_router(router)
app = PropanApp(broker)