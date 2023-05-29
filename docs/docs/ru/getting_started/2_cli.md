# CLI

**Propan** имеет собственный встроенный **CLI** инструмент для вашего максимального комфорта как разработчика.

!!! quote ""
    Спасибо [*typer*](https://typer.tiangolo.com/){target="_blank"} и [*watchfiles*](https://watchfiles.helpmanual.io/){target="_blank"}. Их труд лежит в основе данного инструмента.

<div class="termy">
```console
$ propan --help

Usage: propan [OPTIONS] COMMAND [ARGS]...

  Generate, run and manage Propan apps to greater development experience

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


## Генерация проекта

Чтобы начать новый проект не "с чистого листа", вы можете использовать стандартный шаблон **Propan**

<div class="termy">
```console
$ propan create async rabbit app

Create Propan project template at: ./app
```
</div>

Шаблон включает в себя:

* простой, но рабочий *Dockerfile*
* *docker-compose.yml*, сконфигурированный для разработки
* проект, настроенный для использования *pydantic* в качестве менеджера окружения

## Перезагрузка проекта

Благодаря [*watchfiles*](https://watchfiles.helpmanual.io/){target="_blank"}, написанному на *Rust*, вы можете 
работать со своим проектом легко и непринужденно. Правьте код сколько душе угодно - новая версия уже запущена и ждет ваших запросов!

<div class="termy">
```console
$ propan run app.app.serve:app --reload

2023-04-10 23:39:41,140 INFO     - Started reloader process [115536] using WatchFiles
2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

## Управление окружением

Вы можете передавать любые собственные флаги и опции запуска в **Propan CLI** даже без предварительной их регистрации. Просто используйте их при запуске приложения - и они окажутся прямо в вашем окружении.

Используйте эту опцию для выбора файлов окружения, настройки логирования или на ваше усмотрение.

Для примера передадим файл *.env* в контекст нашего приложения:

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
    Обратите внимение, что параметр `env` был передан в функцию `setup` прямо из командой строки

Все переданные значения могут быть типа `bool`, `str` или `list[str]`.

При этом флаги будут интерпретироваться следующим образом:

```bash
$ propan run app:app --flag       # flag = True
$ propan run app:app --no-flag    # flag = False
$ propan run app:app --my-flag    # my_flag = True
$ propan run app:app --key value  # key = "value"
$ propan run app:app --key 1 2    # key = ["1", "2"]
```
Вы можете использовать их как в отдельности, так и вместе в неограниченном количестве.