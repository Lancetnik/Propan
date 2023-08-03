---
first: In order to test it without running
second: you need to modify the broker with
---

# Testing

To test your app locally or in a CI pipeline, you want to reduce the number of external dependencies.
This allows running a test suite more quickly than when a container with your Message Broker needs to be instantiated within the CI pipeline.

Also, the absence of dependencies helps to avoid test failures that are due to errors in transmitting data to the broker, or accessing the broker too early (when the container is not yet ready to receive connections).

!!! note
    To run asynchronous tests using **pytest**, you need to install extensions.

    You can use, for example, [**pytest-asyncio**](https://pytest-asyncio.readthedocs.io/en/latest/){target="_blank"} or [**anyio**](https://anyio.readthedocs.io/en/stable/testing.html){target="_blank"}

## Broker modification

**Propan** allows you to modify the behavior of your broker so that it passes messages "in memory" without requiring you to discover external dependencies.

Let's imagine we have an application like so:

{% import 'getting_started/test/1.md' as includes with context %}
{{ includes }}

Then make an *RPC* request to check the result of the execution:

{! includes/getting_started/test/2.md !}

!!! note
    When using the test broker this way, it is always possible to perform **RPC** requests even if the broker doesn't support it in regular mode.

## Using fixtures

For large applications to reuse the test broker, you can use the following fixture:

{! includes/getting_started/test/3.md !}

!!! tip
      This approach has a major weakness: Errors that raises inside handler **cannot be captured** inside your tests.

For example, the following test will return `None` and inside the handler, a `pydantic.ValidationError` will be raised:

```python hl_lines="4 6"
{!> docs_src/quickstart/testing/4_suppressed_exc.py !}
```

Also this test will be blocked for `callback_timeout` (default **30** seconds), which can be very annoying when a handler development error occures, and your tests fail with a long timeout of `None`.

## Regular function calling

**Propan** provides the ability to run handler functions as if they were regular functions.

To do this, you need to construct a message using the `build_message`, if it was `publish` (same method signatures), and passe this message to your handler as the single function argument.

{! includes/getting_started/test/4.md !}

That being said, if you want to catch handler exceptions, you need to use the `reraise_exc=True` calling flag:

{! includes/getting_started/test/5.md !}

Thus, **Propan** provides you with a complete toolkit for testing your handlers, from checking *RPC* responses to correctly executing body functions.
