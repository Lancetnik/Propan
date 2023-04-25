from propan import PropanApp, Context
from propan.annotations import ContextRepo

app = PropanApp()

@app.on_startup
async def setup(context: ContextRepo):
    context.set_global("field", 1)

@app.on_startup
async def setup_later(field: int = Context()):
    assert field == 1
