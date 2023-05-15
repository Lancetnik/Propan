# Тестирование

Для того, чтобы протестировать ваше приложение локально, либо в рамках CI пайплайна, вам хочется уменьшить количество внешних зависимостей.
Гораздо проще сразу запустить набор тестов, чем пытаться поднимать контейнер с вашим Брокером Сообщений в рамках CI пайплайна.

Также, отстуствие внешних зависимостей позволит избежать ложного падения тестов, которое может быть связано с ошибками передачи данных до брокера, либо слишком ранним обращением к нему (когда контейнер еще не готов принимать сообщения).

## Модификация брокера

С этой целью **Propan** позволяет модифицировать поведение вашего брокера так, чтобы он передавал сообщения "в памяти", не требуя запуска внешних зависимостей.

Допустим, у нас есть приложение со следующим содержанием:

=== "Redis"
      ```python linenums="1" title="main.py"
      {!> docs_src/quickstart/testing/1_main_redis.py!}
      ```

      Для того, чтобы протестировать его без запуска *Redis*, необходимо модифицировать брокера с помощью `propan.test.TestRedisBroker`:

      ```python linenums="1" title="test_ping.py" hl_lines="1 6"
      {!> docs_src/quickstart/testing/2_test_redis.py!}
      ```

=== "RabbitMQ"
      ```python linenums="1" title="main.py"
      {!> docs_src/quickstart/testing/1_main_rabbit.py!}
      ```

       Для того, чтобы протестировать его без запуска *RabbitMQ*, необходимо модифицировать брокера с помощью `propan.test.TestRabbitBroker`:

      ```python linenums="1" title="test_ping.py" hl_lines="1 6"
      {!> docs_src/quickstart/testing/2_test_rabbit.py!}
      ```

Для тестирования мы сначала должны запустить обработчики наших сообщений: это делается с помощью метода `start`:

=== "Redis"
      ```python hl_lines="2"
      {!> docs_src/quickstart/testing/2_test_redis.py [ln:6-8]!}
      ```

=== "RabbitMQ"
      ```python hl_lines="2"
      {!> docs_src/quickstart/testing/2_test_rabbit.py [ln:6-8]!}
      ```

А затем мы делает *RPC* запрос для того, чтобы проверить результат выполнения:

=== "Redis"
      ```python hl_lines="3"
      {!> docs_src/quickstart/testing/2_test_redis.py [ln:6-8]!}
      ```

=== "RabbitMQ"
      ```python hl_lines="3"
      {!> docs_src/quickstart/testing/2_test_rabbit.py [ln:6-8]!}
      ```

## Использование фикстур

Для больших приложений для переиспользования тестового брокера вы можете использовать фикстуру следующего содержания:

=== "Redis"
      ```python linenums="1" title="test_broker.py" hl_lines="6-10 12"
      {!> docs_src/quickstart/testing/3_conftest_redis.py !}
      ```

=== "RabbitMQ"
      ```python linenums="1" title="test_broker.py" hl_lines="6-10 12"
      {!> docs_src/quickstart/testing/3_conftest_rabbit.py !}
      ```

## Прямой вызов функций

!!! tip
    Данный подход имеет существенный недостаток: ошибки, возникшие внутри обработчика, **не могут быть захвачены** внутри ваших тестов.

Например, следующий тест вернет `None`, а внутри обработчика - возникнет `pydantic.ValidationError`:

=== "Redis"
      ```python hl_lines="4 6"
      {!> docs_src/quickstart/testing/4_suppressed_exc_redis.py !}
      ```

=== "RabbitMQ"
      ```python hl_lines="4 6"
      {!> docs_src/quickstart/testing/4_suppressed_exc_rabbit.py !}
      ```

Также этот тест будет заблокировать на `callback_timeout` (по умолчанию **30** секунд), что может может сильно раздражать, когда внутри разрабатываемого
обработчика возникают ошибки, а ваши тесты отваливаются по длительному таймауту с `None`.

Поэтому **Propan** предоставляет возможность вызывать функции-обработчики напрямую: так, как если бы это были обычные функции.

Для этого вам нужно сконструироваться сообщение с помощью метода `build_message` так, если бы это был `pubslih` (сигнатуры методов совпадают), а затем
передать это сообщение в ваш обработчик в качестве единственного аргумента функции.

=== "Redis"
      ```python linenums="1" hl_lines="6-7" title="test_ping.py"
      {!> docs_src/quickstart/testing/5_build_message_redis.py !}
      ```

=== "RabbitMQ"
      ```python linenums="1" hl_lines="6-7" title="test_ping.py"
      {!> docs_src/quickstart/testing/5_build_message_rabbit.py !}
      ```

При этом, если вы хотите, чтобы захватывать исключения обработчика, вам нужно использовать флаг `reraise_exc=True` при вызове:

=== "Redis"
      ```python linenums="1" hl_lines="9-10" title="test_ping.py"
      {!> docs_src/quickstart/testing/6_reraise_redis.py !}
      ```

=== "RabbitMQ"
      ```python linenums="1" hl_lines="9-10" title="test_ping.py"
      {!> docs_src/quickstart/testing/6_reraise_rabbit.py !}
      ```

Таким образом, **Propan** предоставляет вам полный инструментарий для тестирования ваших обработчиков: от валидации *RPC* ответов до корректно выполнения тела функций.