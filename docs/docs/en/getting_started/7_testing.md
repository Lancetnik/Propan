# Testing

To test your app locally or in a CI pipeline, you want to reduce the number of external dependencies.
Runs a test suite more presently than instantiate a container with your Message Broker within the CI pipeline.

Also, the absence of dependencies helps to avoid tests failure, based on an error in transmitting data to the broker, or accessing broker too early (when the container is not yet ready to receive connection).

## Broker modification

**Propan** allows you to modify the behavior of your broker so that it passes messages "in memory" without requiring you to discover external dependencies.

Let's image we have an application like so:

=== "Redis"
      ```python linenums="1" title="main.py"
      {!> docs_src/quickstart/testing/1_main_redis.py!}
      ```

      In order to test it without running *Redis*, you need to modify the broker with `propan.test.TestRedisBroker`:

      ```python linenums="1" title="test_ping.py" hl_lines="1 6"
      {!> docs_src/quickstart/testing/2_test_redis.py!}
      ```

=== "RabbitMQ"
      ```python linenums="1" title="main.py"
      {!> docs_src/quickstart/testing/1_main_rabbit.py!}
      ```

      In order to test it without running *RabbitMQ*, you need to modify the broker with `propan.test.TestRabbitBroker`:

      ```python linenums="1" title="test_ping.py" hl_lines="1 6"
      {!> docs_src/quickstart/testing/2_test_rabbit.py!}
      ```

This is done with the `start` method:

=== "Redis"
      ```python hl_lines="2"
      {!> docs_src/quickstart/testing/2_test_redis.py [ln:6-8]!}
      ```

=== "RabbitMQ"
      ```python hl_lines="2"
      {!> docs_src/quickstart/testing/2_test_rabbit.py [ln:6-8]!}
      ```

Then make an *RPC* request to check the result of the execution:

=== "Redis"
      ```python hl_lines="3"
      {!> docs_src/quickstart/testing/2_test_redis.py [ln:6-8]!}
      ```

=== "RabbitMQ"
      ```python hl_lines="3"
      {!> docs_src/quickstart/testing/2_test_rabbit.py [ln:6-8]!}
      ```

## Using fixtures

For large applications to reuse the test broker, you can use the following fixture:

=== "Redis"
      ```python linenums="1" title="test_broker.py" hl_lines="6-10 12"
      {!> docs_src/quickstart/testing/3_conftest_redis.py !}
      ```

=== "RabbitMQ"
      ```python linenums="1" title="test_broker.py" hl_lines="6-10 12"
      {!> docs_src/quickstart/testing/3_conftest_rabbit.py !}
      ```

## Regular function calling

!!! tip
      This approach has a major weakness: Errors that raises inside handler **cannot be captured** inside your tests.

For example, the following test will return `None` and inside the handler, a `pydantic.ValidationError` will be raised:

=== "Redis"
      ```python hl_lines="4 6"
      {!> docs_src/quickstart/testing/4_suppressed_exc_redis.py !}
      ```

=== "RabbitMQ"
      ```python hl_lines="4 6"
      {!> docs_src/quickstart/testing/4_suppressed_exc_rabbit.py !}
      ```

Also this test will be blocked for `callback_timeout` (default **30** seconds), which can be very annoying when a handler development error occures, and your tests fail with a long timeout of `None`.

Therefore, **Propan** provides the ability to run handler functions as if they were regular functions.

To do this, you need to construct a message using the `build_message`, if it was `pubslih` (same method signatures), and passe this message to your handler as the single function argument.

=== "Redis"
      ```python linenums="1" hl_lines="6-7" title="test_ping.py"
      {!> docs_src/quickstart/testing/5_build_message_redis.py !}
      ```

=== "RabbitMQ"
      ```python linenums="1" hl_lines="6-7" title="test_ping.py"
      {!> docs_src/quickstart/testing/5_build_message_rabbit.py !}
      ```

That being said, if you want to catch handler exceptions, you need to use the `reraise_exc=True` calling flag:

=== "Redis"
      ```python linenums="1" hl_lines="9-10" title="test_ping.py"
      {!> docs_src/quickstart/testing/6_reraise_redis.py !}
      ```

=== "RabbitMQ"
      ```python linenums="1" hl_lines="9-10" title="test_ping.py"
      {!> docs_src/quickstart/testing/6_reraise_rabbit.py !}
      ```

Thus, **Propan** provides you with a complete toolkit for testing your handlers, from checking *RPC* responses to correctly executing body functions.
