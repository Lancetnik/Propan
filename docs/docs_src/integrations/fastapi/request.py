@app.get("/")
def main(request: Request):
    broker = request.state.broker