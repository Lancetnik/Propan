# Settings and Environment Variables

In many cases your application could need some external settings or configurations, for example Message Broker connection or database credentials.

For this reason it's common to provide them in environment variables that are read by the application.

## Pydantic `Settings`

Fortunately, **Pydantic** provides a great utility to handle these settings coming from environment variables with [Pydantic: Settings management](https://docs.pydantic.dev/latest/usage/pydantic_settings/){.external-link target="_blank"}.

### Install `pydantic-settings`

First, install the `pydantic-settings` package:

<div class="termy">
```console
$ pip install pydantic-settings
---> 100%
```
</div>

!!! info
    In **Pydantic v1** it came included with the main package. Now it is distributed as this independent package so that you can choose to install it or not if you don't need that functionality.

### Create the `Settings` object

Import `BaseSettings` from Pydantic and create a sub-class, very much like with a Pydantic model.

The same way as with Pydantic models, you declare class attributes with type annotations, and possibly default values.

You can use all the same validation features and tools you use for Pydantic models, like different data types and additional validations with `Field()`.

=== "Pydantic v2"
    ```python linenums='1' hl_lines="1 3" title="config.py"
    {!> docs_src/quickstart/settings/settings_base_2.py !}
    ```

=== "Pydantic v1"
    !!! info
        In **Pydantic v1** you would import `BaseSettings` directly from `pydantic` instead of from `pydantic_settings`.

    ```python linenums='1' hl_lines="1 3" title="config.py"
    {!> docs_src/quickstart/settings/settings_base_1.py !}
    ```

Then, when you create an instance of that `Settings` class (in this case, in the `settings` object), Pydantic will read the environment variables in a case-insensitive way, so, an upper-case variable `APP_NAME` will still be read for the attribute `app_name`.

Next it will convert and validate the data. So, when you use that `settings` object, you will have data of the types you declared (e.g. `items_per_user` will be an `int`).

### Use the `settings`

Then you can use the new `settings` object in your application:

```python linenums='1' hl_lines="4 6 9" title="serve.py"
{!> docs_src/quickstart/settings/usage.py !}
```

### Run the application

Next, you would run the application passing the configurations as environment variables, for example you could set an `URL`:

<div class="termy">
```console
$ URL="amqp://guest:guest@localhost:5672" propan run serve:app
```
</div>

!!! tip
    To set multiple env vars for a single command just separate them with a space, and put them all before the command.

## Reading a `.env` file

If you have many settings that possibly change a lot, maybe in different environments, it might be useful to put them on a file and then read them from it as if they were environment variables.

This practice is common enough that it has a name, these environment variables are commonly placed in a file `.env`, and the file is called a "dotenv".

!!! tip
    A file starting with a dot (`.`) is a hidden file in Unix-like systems, like Linux and macOS.

    But a dotenv file doesn't really have to have that exact filename.

Pydantic has support for reading from these types of files using an external library. You can read more at [Pydantic Settings: Dotenv (.env) support](https://docs.pydantic.dev/latest/usage/pydantic_settings/#dotenv-env-support){.external-link target="_blank"}.

!!! tip
    For this to work, you need to `pip install python-dotenv`.

### The `.env` file

You could have a `.env` file with:

```bash
URL="amqp://guest:guest@localhost:5672"
QUEUE="test-queue"
```

### Read settings from `.env`

And then update your `config.py` with:

```python linenums='1' hl_lines="1 7"
{!> docs_src/quickstart/settings/settings_env.py !}
```

This way you are able to specify different `.env` files right from your terminal. It can be extremely helpful in testing/production cases.

!!! note
    By default Pydantic tries to find `.env` field in this case, but it is OK, if there are no any `.env` file. Pydantic just use a default fields values.

### Choose `.env` file at start

Now you can run the apllication with various `.env` files like:

<div class="termy">
```console
$ ENV=.local.env propan run serve:app
```
</div>

Or, probably, production

<div class="termy">
```console
$ ENV=.production.env propan run serve:app
```
</div>

Or even test environment

<div class="termy">
```console
$ ENV=.test.env pytest
```
</div
