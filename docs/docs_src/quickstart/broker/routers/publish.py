@app.after_startup
async def publish_test():
    await broker.publish("user-fake-uuid", "user/created")