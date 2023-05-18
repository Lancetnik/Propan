def test_create_propject(rabbit_async_project):
    assert rabbit_async_project.exists()
