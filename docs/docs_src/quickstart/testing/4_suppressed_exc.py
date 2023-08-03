async def test_publish(test_broker):
    r = await test_broker.publish(
        {"msg": "ping"}, "ping",
        callback=True, callback_timeout=1
    )
    assert r == None