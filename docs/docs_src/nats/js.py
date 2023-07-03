from propan import PropanApp, NatsJSBroker
from propan.annotations import NatsJS

broker = NatsJSBroker()
app = PropanApp(broker)

@app.after_startup
async def example(js: NatsJS):
    # JS Key-Value Storage
    storage = await js.create_key_value(bucket="propan_kv")

    await storage.put("hello", b"propan!")
    assert (await storage.get("hello")) == b"propan!"

    # JS Object Storage
    storage = await js.create_object_sotre("propan-obs")

    obj_name = "file.mp4"
    with open(obj_name) as f:
        await storage.put(obj_name, f)

    with open(f"copy-{obj_name}") as f:
        await storage.get(obj_name, f)
