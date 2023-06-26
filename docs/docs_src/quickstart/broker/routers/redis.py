from propan import PropanApp, RedisBroker, RedisRouter

router = RedisRouter(prefix="user/")

@router.handle("created")
async def handle_user_created_event(user_id: str):
    ...

broker = RedisBroker()
broker.include_router(router)
app = PropanApp(broker)