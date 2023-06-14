import json
from typing import Any, Callable, Dict, Optional, Union

from propan.asyncapi import AsyncAPISchema
from propan.cli.docs.gen import schema_to_json


def serve_docs(
    schema: str = "",
    host: str = "0.0.0.0",
    port: int = 8000,
    raw_schema: Optional[AsyncAPISchema] = None,
) -> None:
    if not any((schema, raw_schema)):
        raise ValueError("You should set `shema` or `raw_schema`")

    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()

    app.get("/")(asyncapi_html_endpoint(schema, raw_schema))

    if raw_schema is not None:
        app.get("/asyncapi.json")(download_json_endpoint(raw_schema))

    app.get("/asyncapi.yaml")(download_yaml_endpoint(schema))
    uvicorn.run(app, host=host, port=port)


def download_yaml_endpoint(schema: str) -> Callable[[], Any]:
    from fastapi.responses import Response

    def download_yaml() -> Response:
        return Response(
            content=schema,
            headers={
                "Content-Type": "application/octet-stream",
            },
        )

    return download_yaml


def download_json_endpoint(raw_schema: AsyncAPISchema) -> Callable[[], Any]:
    from fastapi.responses import Response

    def download_json() -> Response:
        return Response(
            content=json.dumps(
                schema_to_json(raw_schema),
                indent=4,
            ),
            headers={
                "Content-Type": "application/octet-stream",
            },
        )

    return download_json


def asyncapi_html_endpoint(
    schema: str, raw_schema: Optional[AsyncAPISchema] = None
) -> Callable[[], Any]:
    from fastapi.responses import HTMLResponse

    def asyncapi(
        sidebar: bool = True,
        info: bool = True,
        servers: bool = True,
        operations: bool = True,
        messages: bool = True,
        schemas: bool = True,
        errors: bool = True,
        expandMessageExamples: bool = True,
    ) -> HTMLResponse:
        return HTMLResponse(
            content=get_asyncapi_html(
                schema,
                sidebar=sidebar,
                info=info,
                servers=servers,
                operations=operations,
                messages=messages,
                schemas=schemas,
                errors=errors,
                expand_message_examples=expandMessageExamples,
                title=raw_schema.info.title if raw_schema else "Propan",
            )
        )

    return asyncapi


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
    title: str = "Propan",
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

    return (
        """
    <!DOCTYPE html>
    <html>
        <head>
    """
        f"""
        <title>{title} AsyncAPI</title>
    """
        """
        <link rel="icon" href="https://www.asyncapi.com/favicon.ico">
        <link rel="icon" type="image/png" sizes="16x16" href="https://www.asyncapi.com/favicon-16x16.png">
        <link rel="icon" type="image/png" sizes="32x32" href="https://www.asyncapi.com/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="194x194" href="https://www.asyncapi.com/favicon-194x194.png">
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
        <script>
    """
        f"""
            AsyncApiStandalone.render({json.dumps(config)}, document.getElementById('asyncapi'));
    """
        """
        </script>
        </body>
    </html>
    """
    )
