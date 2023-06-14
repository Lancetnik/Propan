from propan.fastapi import RabbitRouter

router = RabbitRouter(
    schema_url="/asyncapi",
    include_in_schema=True,
)