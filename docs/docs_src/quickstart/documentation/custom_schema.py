from propan import PropanApp, RabbitBroker
from propan.asyncapi.main import AsyncAPISchema
from propan.cli.docs.gen import gen_app_schema_json, gen_app_schema_yaml, get_app_schema
from propan.cli.docs.serving import get_asyncapi_html

broker = RabbitBroker()
app = PropanApp(broker)

schema: AsyncAPISchema = get_app_schema(app)
json_schema = gen_app_schema_json(app)
yaml_schema = gen_app_schema_yaml(app)
html = get_asyncapi_html(yaml_schema)