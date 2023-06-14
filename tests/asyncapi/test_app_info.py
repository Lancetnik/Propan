from propan import PropanApp, RabbitBroker
from propan.asyncapi import AsyncAPIContact, AsyncAPILicense
from propan.cli.docs.gen import gen_app_schema_json


def test_app_default_info():
    schema = gen_app_schema_json(PropanApp(RabbitBroker()))
    assert schema["info"] == {
        "description": "",
        "title": "Propan",
        "version": "0.1.0",
    }


def test_app_base_info():
    schema = gen_app_schema_json(
        PropanApp(
            RabbitBroker(),
            title="My App",
            description="description",
            version="1.0.0",
        )
    )
    assert schema["info"] == {
        "description": "description",
        "title": "My App",
        "version": "1.0.0",
    }


def test_app_detail_info():
    schema = gen_app_schema_json(
        PropanApp(
            RabbitBroker(),
            title="My App",
            description="description",
            version="1.0.0",
            license=AsyncAPILicense(name="MIT", url="http://mit.com"),
            contact=AsyncAPIContact(
                name="Developer",
                url="http://my-domain.com",
                email="my-domain@gmail.com",
            ),
        )
    )
    assert schema["info"] == {
        "contact": {
            "email": "my-domain@gmail.com",
            "name": "Developer",
            "url": "http://my-domain.com",
        },
        "description": "description",
        "license": {
            "name": "MIT",
            "url": "http://mit.com",
        },
        "title": "My App",
        "version": "1.0.0",
    }
