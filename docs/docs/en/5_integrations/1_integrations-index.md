# INTEGRATIONS

**Propan** brokers are very easy to integrate with any of your applications:
it is enough to initialize the broker at startup and close it correctly at the end of
your application.

Most HTTP frameworks have built-in lifecycle hooks for this.

=== "Fastapi"
    !!! tip
        If you want to use **Propan** in conjunction with **Facetapi**, perhaps you should use a special
        [plugin](../2_fastapi-plugin/)

    ```python hl_lines="7 14 16 19-21"
    {!> ../examples/http_frameworks_integrations/fastapi.py [ln:5-29]!}
    ```

=== "Aiohttp"
    ```python hl_lines="5 8-10 14 18"
    {!> ../examples/http_frameworks_integrations/aiohttp.py [ln:5-35]!}
    ```

=== "Blacksheep"
    ```python hl_lines="8 11-13 18 23"
    {!> ../examples/http_frameworks_integrations/blacksheep.py [ln:5-31]!}
    ```

=== "Falcon"
    ```python hl_lines="6 9-11 28 31"
    {!> ../examples/http_frameworks_integrations/falcon.py [ln:5-39]!}
    ```

=== "Quart"
    ```python hl_lines="5 10-12 17 22"
    {!> ../examples/http_frameworks_integrations/quart.py [ln:5-30]!}
    ```

=== "Sanic"
    ```python hl_lines="7 10-12 17 22"
    {!> ../examples/http_frameworks_integrations/sanic.py [ln:5-30]!}
    ```

However, even if such a hook is not provided, you can do it yourself.

=== "Tornado"
    ```python hl_lines="7 10-12 32-36"
    {!> ../examples/http_frameworks_integrations/tornado.py [ln:5-43]!}
    ```