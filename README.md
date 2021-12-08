Propan создан, чтобы создание микросервисов вокруг RabbitMQ было как никогда простым

Основные особенности:

* **Окружение**: максимальное удоство для работы с настройками проекта.
* **Скорость разработки**: один декоратор - один потребитель на очередь.
* **Обработка входных параметров**: автоматическая сериализация сообщений из RabbitMQ в соответствии с аннотацией типов.

## Окружение

Python 3.9+

## Примеры

### Создание проекта

* Создайте проект с помощью `propan --start test_project`
* Перейдите в директорию проекта `cd test_project`
* Создайте `app/config/settings.py` с данными для подключения к RabbitMQ

```Python
RABBIT_HOST = "127.0.0.1"
RABBIT_LOGIN = "guest"
RABBIT_PASSWORD = "guest"
RABBIT_VIRTUALHOST = "/"
```

* Настройки проекта также можно указывать в `app/config/config.yml` файле

```yml
RABBIT:
    host: '127.0.0.1'
    login: 'guest'
    password: 'guest'
    virtualhost: /
```

В таком случае переменные из .yml файла будут транслированы в настройки в верхнем регистре

```yml
Rabbit:
    host: '127.0.0.1'
```
Аналогичен
```yml
RABBIT_HOST: '127.0.0.1'
```

Проект также автоматически берет переменные из окружения при наличии совпадений в названии переменных из .yml файла
* Таким образом приоритеты использования переменных в конфликтных ситуациях расставлены следующим образом: environment > config.yml > settings.py
* При попытке обратиться к переменной, которой нет в настройках, propan выдаст warning и `None` в качестве значения
* `.yml` файла можно переключать при запуске с помощью флага `--config=prod.yml` или `-C prod.yml`
    * в таком случае все используемые `.yml` файлы должны находиться в директории `app/config/`


* После указания данных для подключения к RabbitMQ создадим коннектор в `app/dependencies.py`

```Python
import asyncio

from propan.config.lazy import settings

from propan.event_bus.model.bus_connection import ConnectionData
from propan.event_bus.adapter.rabbit_queue import AsyncRabbitQueueAdapter


loop = asyncio.get_event_loop()


queue_adapter = AsyncRabbitQueueAdapter()  # инстанс подключения
loop.run_until_complete(queue_adapter.connect(
    connection_data=ConnectionData(
        host = settings.RABBIT_HOST,
        login = settings.RABBIT_LOGIN,
        password = settings.RABBIT_PASSWORD,
        virtualhost = settings.RABBIT_VIRTUALHOST,
    ),
    loop=loop
))  # инициализация подключения
loop.run_until_complete(queue_adapter.init_channel(
    max_consumers=settings.MAX_CONSUMERS
))  # инициализация канала
```
    * Глобальные найстроки используются во всех случаях, когда необходимо получить доступ к константам проекта (инициализируются как указано выше при старте приложения)
```Python
from propan.config.lazy import settings
```
`settings.MAX_CONSUMERS` указывается при запуске проекта с помощью флага `--workers=10` или `-W 10` (10-значение по умолчанию) и определяет допустимое количество одновременно обрабатываемых сообщений

* После создания `queue_adapter` создадим `PropanApp` в `app/serve.py`
```Python
from propan.app import PropanApp

from .dependencies import queue_adapter


app = PropanApp(queue_adapter=queue_adapter)


@app.queue_handler(queue_name="test_queue")
async def base_handler(message):
    print(message)
```

* Запуск проекта осуществляется с помощью команды `propan app.serve:app`, где `app.serve` - путь к файлу serve, а `app` - название экземпляра `PropanApp` в коде.
    * Запуск по умолчанию: `propan app.serve:app -C config.yml -W 10`
    * Используйте флаг `--reload` для запуска проекта в тестовом режиме с автоматической перезагрузкой при изменении файлов