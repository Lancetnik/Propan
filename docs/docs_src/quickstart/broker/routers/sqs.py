from propan import PropanApp, SQSBroker, SQSRouter

router = SQSRouter(prefix="user/")

@router.handle("created")
async def handle_user_created_event(user_id: str):
    ...

broker = SQSBroker()
broker.include_router(router)
app = PropanApp(broker)