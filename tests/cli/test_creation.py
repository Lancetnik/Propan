def test_create_rabbit_project(rabbit_async_project):
    assert rabbit_async_project.exists()


def test_create_redis_project(redis_async_project):
    assert redis_async_project.exists()


def test_create_nats_project(nats_async_project):
    assert nats_async_project.exists()


def test_create_nats_js_project(nats_js_async_project):
    assert nats_js_async_project.exists()


def test_create_kafka_project(kafka_async_project):
    assert kafka_async_project.exists()


def test_create_sqs_project(sqs_async_project):
    assert sqs_async_project.exists()
