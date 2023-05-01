# CONTEXT

**Propan** stores the context of the application and each request. You can access them using a special class `Context`.

```python linenums="1" hl_lines="4"
{!> docs_src/quickstart/dependencies/context/1_context.py !}
```

## Existing fields

**Context** already contains some global objects that you can always access:

* **app** - the `PropanApp` object of your application
* **broker** - current broker
* **context** - the context itself, in which you can write your own fields
* **logger** - logger used for your broker (tags messages with *message_id*)
* **message** - raw message (if you need access to it)

At the same time, thanks to `contextlib.ContextVar`, **message** always corresponds to the context the current handler process.

## Access to context fields

By default, as in the example above, the context searches for an object based on the argument name.

```python linenums="1" hl_lines="6-10"
{!> docs_src/quickstart/dependencies/context/2_context.py !}
```

### Access by name

Sometimes you may need to use a different name for the argument (not the one under which it is stored in the context). Or even get access not to the whole object, but only to its field or method. To do this, just specify by name what you want to get - and the context will provide you with the wished object.

```python linenums="1" hl_lines="6-8"
{!> docs_src/quickstart/dependencies/context/3_context.py !}
```

### Annotated

The default method is not very convenient if you need to use the same context field throughout the project. Also, it requires explicit annotation of the type of the incoming argument if we want to use the auto-completion of our IDE. In order to avoid long import chains and code duplication, `Context` is fully compatible with `typing.Annotated`.

```python linenums="1" hl_lines="4 9"
{!> docs_src/quickstart/dependencies/context/4_context.py !}
```

For your convenience, **Propan** already contains annotations for existing context fields. You can import them and use at your code.

```python linenums="1" hl_lines="1 6-10"
{!> docs_src/quickstart/dependencies/context/5_context.py !}
```

### Default values

If you try to access a field that does not exist in the global context, you will get the `pydantic.ValidationError` exception.

However, you can set the default value if you feel the need.

```python linenums="1" hl_lines="6 8"
{!> docs_src/quickstart/dependencies/context/6_context.py !}
```

### Casting context types

By default, context fields are **NOT CAST** to the type specified in their annotation. If you need this functionality, you can set the appropriate flag.

```python linenums="1" hl_lines="6 8"
{!> docs_src/quickstart/dependencies/context/7_context.py !}
```

## Declaration of context fields

### Globally

To declare the context fields, you need to call the `context.set_global` method with an indication of the key by which the object will be placed in the context.

```python linenums="1" hl_lines="6 8"
{!> docs_src/quickstart/dependencies/context/8_context.py !}
```

In this case, the field becomes a global context field: it does not depend on the current message handler (unlike `message`)

To remove a field from the context use `reset_global`
```python
context.reset_global("my_key")
```

### Locally

To set the local context (it will act in all functions called inside it), use the context manager `scope`

```python linenums="1" hl_lines="9 13"
{!> docs_src/quickstart/dependencies/context/9_context.py !}
```

Also, you can set the context yourself: then it will act within the current call stack until you clear it.

```python linenums="1" hl_lines="9 11 13"
{!> docs_src/quickstart/dependencies/context/10_context.py !}
```

## Use in other functions

By default, the context is available in the same place as `Depends`:

* at life cycle hooks
* message handlers
* dependencies

### Depends

When using `Context` in `Depends`, there is no need to write additional code: like nested `Depends`, `Context` is also available by default. 

```python linenums="1" hl_lines="5 7 10"
{!> docs_src/quickstart/dependencies/context/11_context.py !}
```

### Normal functions

To use context at other functions use the decorator `@apply_types`. This case, the called function context will correspond to the context of the event handler from which it was called.

```python linenums="1" hl_lines="5 7 10"
{!> docs_src/quickstart/dependencies/context/12_context.py !}
```

In the example above, we did not pass the `logger` function at calling, it was placed out of context.