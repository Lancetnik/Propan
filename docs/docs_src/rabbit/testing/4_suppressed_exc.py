def test_publish(test_broker):
    r = await test_broker.publish(
        {"msg": "ping"}, queue="ping",
        callback=True, callback_timeout=1
    )
    assert r == None