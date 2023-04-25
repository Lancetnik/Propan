from propan import apply_types, Context
from propan.annotations import ContextRepo

@broker.hanlde("test")
async def handler(
    body: dict,
    context: ContextRepo
):
    with context.scope("local", 1):
        nested_function()

@apply_types
def nested_function(local = Context()):
    assert local == 1