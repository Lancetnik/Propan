---
run_docker: Для работы проекта запустите тестовый контейнер с брокером
---

# Быстрый старт

Для начала, установите фрейморк через `pip`:

{% import 'getting_started/index/install.md' as includes with context %}
{{ includes }}

### Базовое использование

Создайте приложение со следующим кодом в `serve.py` файле:

{! includes/getting_started/index/01_base.md !}

И просто запустите его:

<div class="termy">
```console
$ propan run serve:app

2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

---

## Готовый шаблон проекта

Вы можете сгенерировать готовый к использованию шаблон проекта с помощью **Propan CLI**:

<div class="termy">
```console
$ propan create async [broker] [projectname]
Create Propan project template at: /home/user/projectname
```
</div>

!!! note
    Для запуска, шаблон требует установки `pydantic[dotenv]`

А теперь просто запустите сгенерированный проект

<div class="termy">
```console
### Run rabbimq first
$ docker compose --file [projectname]/docker-compose.yaml up -d [broker]

### Run project
$ propan run [projectname].app.serve:app --env=.env --reload

2023-04-10 23:39:41,140 INFO     - Started reloader process [115536] using WatchFiles
2023-04-10 23:39:41,145 INFO     - Propan app starting...
2023-04-10 23:39:41,151 INFO     - `base_handler` waiting for messages
2023-04-10 23:39:41,152 INFO     - Propan app started successfully! To exit press CTRL+C
```
</div>

Наслаждайтесь новым опытом разработки!

??? tip "Не забудьте остановить тестовый контейнер"
    ```bash
    docker container stop test-mq
    ```