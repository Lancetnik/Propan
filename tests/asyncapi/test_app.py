from propan import PropanApp
from propan.asyncapi.generate import get_app_schema
from propan.asyncapi.schema import Contact, ExternalDocs, License, Tag
from propan.kafka import KafkaBroker


def test_base():
    schema = get_app_schema(PropanApp(KafkaBroker())).to_jsonable()

    assert schema == {
        "asyncapi": "2.6.0",
        "channels": {},
        "components": {"messages": {}, "schemas": {}},
        "defaultContentType": "application/json",
        "info": {"description": "", "title": "Propan", "version": "0.1.0"},
        "servers": {
            "development": {
                "protocol": "kafka",
                "protocolVersion": "auto",
                "url": "localhost",
            }
        },
    }


def test_with_name():
    schema = get_app_schema(
        PropanApp(
            KafkaBroker(),
            title="My App",
            version="1.0.0",
            description="Test description",
        )
    ).to_jsonable()

    assert schema == {
        "asyncapi": "2.6.0",
        "channels": {},
        "components": {"messages": {}, "schemas": {}},
        "defaultContentType": "application/json",
        "info": {
            "description": "Test description",
            "title": "My App",
            "version": "1.0.0",
        },
        "servers": {
            "development": {
                "protocol": "kafka",
                "protocolVersion": "auto",
                "url": "localhost",
            }
        },
    }


def test_full():
    schema = get_app_schema(
        PropanApp(
            KafkaBroker(),
            title="My App",
            version="1.0.0",
            description="Test description",
            license=License(name="MIT", url="https://mit.com/"),
            terms_of_service="https://my-terms.com/",
            contact=Contact(name="support", url="https://help.com/"),
            tags=(Tag(name="some-tag", description="experimental"),),
            identifier="some-unique-uuid",
            external_docs=ExternalDocs(
                url="https://extra-docs.py/",
            ),
        )
    ).to_jsonable()

    assert schema == {
        "asyncapi": "2.6.0",
        "channels": {},
        "components": {"messages": {}, "schemas": {}},
        "defaultContentType": "application/json",
        "externalDocs": {"url": "https://extra-docs.py/"},
        "id": "some-unique-uuid",
        "info": {
            "contact": {"name": "support", "url": "https://help.com/"},
            "description": "Test description",
            "license": {"name": "MIT", "url": "https://mit.com/"},
            "termsOfService": "https://my-terms.com/",
            "title": "My App",
            "version": "1.0.0",
        },
        "servers": {
            "development": {
                "protocol": "kafka",
                "protocolVersion": "auto",
                "url": "localhost",
            }
        },
        "tags": [{"description": "experimental", "name": "some-tag"}],
    }


def test_full_dict():
    schema = get_app_schema(
        PropanApp(
            KafkaBroker(),
            title="My App",
            version="1.0.0",
            description="Test description",
            license={"name": "MIT", "url": "https://mit.com/"},
            terms_of_service="https://my-terms.com/",
            contact={"name": "support", "url": "https://help.com/"},
            tags=({"name": "some-tag", "description": "experimental"},),
            identifier="some-unique-uuid",
            external_docs={
                "url": "https://extra-docs.py/",
            },
        )
    ).to_jsonable()

    assert schema == {
        "asyncapi": "2.6.0",
        "channels": {},
        "components": {"messages": {}, "schemas": {}},
        "defaultContentType": "application/json",
        "externalDocs": {"url": "https://extra-docs.py/"},
        "id": "some-unique-uuid",
        "info": {
            "contact": {"name": "support", "url": "https://help.com/"},
            "description": "Test description",
            "license": {"name": "MIT", "url": "https://mit.com/"},
            "termsOfService": "https://my-terms.com/",
            "title": "My App",
            "version": "1.0.0",
        },
        "servers": {
            "development": {
                "protocol": "kafka",
                "protocolVersion": "auto",
                "url": "localhost",
            }
        },
        "tags": [{"description": "experimental", "name": "some-tag"}],
    }
