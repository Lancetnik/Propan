# INTEGRATIONS

Брокеров **Propan** очень легко интегрировать с любым вашим приложением:
для этого достаточно инициализировать брокера при старте и корректно закрыть вместе с окончанием работы
вашего приложения.

Большинство HTTP ферймворков имеют для этого встроенные хуки жизненного цикла.

=== "Fastapi"
    !!! tip
        Если вы хотите использовать **Propan** совместно с **FastAPI**, возможно, вам стоит использовать специальный
        [плагин](../2_fastapi-plugin/)
        
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

Однако, даже если такого хука не предусмотрено, вы можете сделать это самостоятельно.

=== "Tornado"
    ```python hl_lines="7 10-12 32-36"
    {!> ../examples/http_frameworks_integrations/tornado.py [ln:5-43]!}
    ```