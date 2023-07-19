# CLI

**Propan** has its own built-in **CLI** tool for your maximum comfort as a developer.

!!! quote ""
    Thanks to [*typer*](https://typer.tiangolo.com/){target="_blank"} and [*watchfiles*](https://watchfiles.helpmanual.io/){target="_blank"}. Their work is the basis of this tool.

<div class="termy">
```console
$ propan --help

Usage: propan [OPTIONS] COMMAND [ARGS]...

  Generate, run, and manage Propan apps for greater development experience

Options:
  --version             Show current platform, python and propan version
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  --help                Show this message and exit.

Commands:
  create  Create a new Propan project at [APPNAME] directory
  run     Run [MODULE:APP] Propan application
```
</div>


## Project generation

To start a new project template, you can use the standard template **Propan**:

<div class="termy">
```console
$ propan create async rabbit app

Create Rabbit Propan project template at: ./app
```
</div>

The template includes:

* a simple yet working *Dockerfile*
* *docker-compose.yml* configured for development
* a project configured to use *pydantic* as the environment manager

## Reloading the project

Thanks to [*watchfiles*](https://watchfiles.helpmanual.io/){target="_blank"}, written in *Rust*, you can
work with your project easily. Edit the code as much as you like - the new version has already been launched and is waiting for your requests!

<div class="termy">
```console
$ propan run app.app.serve:app --reload

2023-04-10 23:39:41,140 INFO     - Started reloader process [115536] using WatchFiles
2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

## Environment Management

You can pass any custom flags and launch options to the **Propan CLI** even without first registering them. Just use them when launching the application - and they will be right in your environment.

Use this option to select environment files, configure logging, or at your discretion.

For example, we will pass the *.env* file to the context of our application:

<div class="termy">
```console
$ propan run serve:app --env=.env.dev

2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

{! includes/getting_started/cli/01_context.md !}

!!! note
    Note that the `env` parameter was passed to the `setup` function directly from the command line

All passed values can be of type `bool`, `str` or `list[str]`.

In this case, the flags will be interpreted as follows:

```bash
$ propan run app:app --flag       # flag = True
$ propan run app:app --no-flag    # flag = False
$ propan run app:app --my-flag    # my_flag = True
$ propan run app:app --key value  # key = "value"
$ propan run app:app --key 1 2    # key = ["1", "2"]
```
You can use them both individually and together in unlimited quantities.