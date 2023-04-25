from propan import PropanApp, Context, NatsBroker
from propan.annotations import ContextRepo

broker = NatsBroker("nats://localhost:4222")
app = PropanApp(broker)

ml_models = {}  # fake ML model

def fake_answer_to_everything_ml_model(x: float):
    return x * 42

@app.on_startup
async def setup_model(context: ContextRepo):
    # Load the ML model
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    context.set_global("model", ml_models)

@app.on_shutdown
async def shutdown_model(model: dict = Context()):
    # Clean up the ML models and release the resources
    model.clear()

@app.get("/test")
async def predict(x: float, model = Context()):
    result = model["answer_to_everything"](x)
    return {"result": result}