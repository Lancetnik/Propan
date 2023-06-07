import json
from typing import Any, Dict, NoReturn, Union


def serve_docs(
    schema: str,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> None:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def read_items(
        sidebar: bool = True,
        info: bool = True,
        servers: bool = True,
        operations: bool = True,
        messages: bool = True,
        schemas: bool = True,
        errors: bool = True,
        expandMessageExamples: bool = True,
    ) -> str:
        return get_asyncapi_html(
            schema,
            sidebar=sidebar,
            info=info,
            servers=servers,
            operations=operations,
            messages=messages,
            schemas=schemas,
            errors=errors,
            expand_message_examples=expandMessageExamples,
        )

    uvicorn.run(app, host=host, port=port)


def get_asyncapi_html(
    schema: Union[str, Dict[str, Any]],
    sidebar: bool = True,
    info: bool = True,
    servers: bool = True,
    operations: bool = True,
    messages: bool = True,
    schemas: bool = True,
    errors: bool = True,
    expand_message_examples: bool = True,
) -> str:
    config = {
        "schema": schema,
        "config": {
            "show": {
                "sidebar": sidebar,
                "info": info,
                "servers": servers,
                "operations": operations,
                "messages": messages,
                "schemas": schemas,
                "errors": errors,
            },
            "expand": {
                "messageExamples": expand_message_examples,
            },
            "sidebar": {
                "showServers": "byDefault",
                "showOperations": "byDefault",
            },
        },
    }

    return """
    <!DOCTYPE html>
    <html>
        <head>
        <title>Propan AsyncAPI</title>
        <link rel="stylesheet" href="https://unpkg.com/@asyncapi/react-component@1.0.0-next.46/styles/default.min.css">
        </head>

        <style>
        html {
            font-family: ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica Neue,Arial,Noto Sans,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol,Noto Color Emoji;
            line-height: 1.5;
        }
        </style>

        <body>
        <div id="asyncapi"></div>

        <script src="https://unpkg.com/@asyncapi/react-component@1.0.0-next.47/browser/standalone/index.js"></script>
    """ + f"""
        <script>
            AsyncApiStandalone.render({json.dumps(config)}, document.getElementById('asyncapi'));
        </script>
        </body>
    </html>
    """
