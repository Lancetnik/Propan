# INTEGRATIONS

Брокеров **Propan** очень легко интегрировать с любым вашим приложением:
для этого достаточно инициализировать брокера при старте и корректно закрыть вместе с окончанием работы
вашего приложения.

Большинство HTTP ферймворков имеют для этого встроенные хуки жизненного цикла.

=== "FastAPI"
    !!! tip
        Если вы хотите использовать **Propan** совместно с **FastAPI**, возможно, вам стоит использовать специальный
        [плагин](../2_fastapi-plugin/)
        
    ```python hl_lines="6 13 15 18-20" linenums="1"
    {!> docs_src/integrations/http_frameworks_integrations/fastapi.py [ln:5-29]!}
    ```

=== "Aiohttp"
    ```python hl_lines="4 7-9 13 17" linenums="1"
    {!> docs_src/integrations/http_frameworks_integrations/aiohttp.py [ln:5-35]!}
    ```

=== "Blacksheep"
    ```python hl_lines="7 10-12 17 22" linenums="1"
    {!> docs_src/integrations/http_frameworks_integrations/blacksheep.py [ln:5-31]!}
    ```

=== "Falcon"
    ```python hl_lines="5 8-10 27 30" linenums="1"
    {!> docs_src/integrations/http_frameworks_integrations/falcon.py [ln:5-39]!}
    ```

=== "Quart"
    ```python hl_lines="4 9-11 16 21" linenums="1"
    {!> docs_src/integrations/http_frameworks_integrations/quart.py [ln:5-30]!}
    ```

=== "Sanic"
    ```python hl_lines="6 9-11 16 21" linenums="1"
    {!> docs_src/integrations/http_frameworks_integrations/sanic.py [ln:5-30]!}
    ```

Однако, даже если такого хука не предусмотрено, вы можете сделать это самостоятельно.

=== "Tornado"
    ```python hl_lines="6 9-11 31-35" linenums="1"
    {!> docs_src/integrations/http_frameworks_integrations/tornado.py [ln:5-43]!}
    ```