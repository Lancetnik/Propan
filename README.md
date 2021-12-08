Propan существует, чтобы максимально упростить для вас создание микросервисов вокруг RabbitMQ

Основные особенности:

* **Окружение**: максимальное удоство для работы с настройками проекта.
* **Скорость разработки**: один декоратор - один потребитель на очередь.
* **Обработка входных параметров**: автоматическая сериализация сообщений из RabbitMQ в соответствии с аннотацией типов.
* **Расширяемость**: возможность создавать собственные классы-реализации интерфейсов Propan.
* **Инъекция зависимостей**: единый подход к работе с зависимостям во всем проекте.

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

В таком случае переменные из `.yml` файла будут транслированы в настройки в верхнем регистре

```yml
Rabbit:
    host: '127.0.0.1'
```
Аналогичен
```yml
RABBIT_HOST: '127.0.0.1'
```

Проект также автоматически берет переменные из окружения при наличии совпадений в названии переменных из `.yml` файла
* Таким образом приоритеты использования переменных в конфликтных ситуациях расставлены следующим образом: `environment` > `config.yml` > `settings.py`
* При попытке обратиться к переменной, которой нет в настройках, propan выдаст warning и `None` в качестве значения
* `.yml` файлы можно переключать при запуске с помощью флага `--config=prod.yml` или `-C prod.yml`
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
Глобальные найстроки используются во всех случаях, когда необходимо получить доступ к константам проекта (инициализируются как указано выше при старте приложения)
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

* Запуск проекта осуществляется с помощью команды `propan app.serve:app`
    * `app.serve` - путь к файлу serve, а `app` - название экземпляра `PropanApp` в коде.
    * Запуск по умолчанию: `propan app.serve:app -C config.yml -W 10`
    * Используйте флаг `--reload` для запуска проекта в тестовом режиме с автоматической перезагрузкой при изменении файлов


### Сериализация входных параметров

* Так как входящие значения RabbitMQ представляют из себя строку, для сериализации входных параметров Propan использует аннотацию типов

```Python
app = PropanApp(
    queue_adapter=queue_adapter,
    apply_types=True
)

@app.queue_handler(queue_name="test_queue")
async def base_handler(user_id: int):  # приведение входного значения к типу int
    print(message)
```
Использование глобальной опции `apply_types=True` включит сериализацию входных параметров для всех handler'ов приложения

* Для использования сериализации в отдельных handler'ах необходимо использовать специальный декоратор `apply_types`

```Python
from propan.annotations.decorate import apply_types

app = PropanApp(queue_adapter=queue_adapter)


@app.queue_handler(queue_name="test_queue")
@apply_types
async def base_handler(user_id: int):
    print(message)
```
* Замечания
    * в таком случае декоратор `apply_types` должен располагаться перед декораторами `app`
    * функция-handler всегда должна принимать на вход один аргумент
    * функция-handler не должна иметь аннотации результата выполнения  `->`

* Для сериализации более сложных объектов возможно использование классов-оберток над `pydantic`

```Python
from typing import Optional

from propan.annotations.models import MessageModel

app = PropanApp(
    queue_adapter=queue_adapter,
    apply_types=True
)

class User(MessageModel):
    username: str
    user_id: Optional[int]

@app.queue_handler(queue_name="test_queue")
async def base_handler(user: User):
    print(user)
```

### Логирование

Все классы Propan, выводящие служебную информацию требуют для этого любой экземпляр logger'a, являющегося реализацией интерфейса `propan.logger.model.usecase.LoggerUsecase`.
Рекомендуется использовать экземпляр этого класса во всем проекте, инициализируя его в `app/dependencies.py`.

```Python
from propan.logger.adapter.loguru_usecase import LoguruAdapter

logger = LoguruAdapter()
queue_adapter = AsyncRabbitQueueAdapter(
    logger=logger
)
```
* По умолчанию во всех классах Propan используется `propan.logger.adapter.empty.EmptyLogger`

Также возможно построение цепочки обработки logger'ов путем использования в качестве экземпляра logger класса `propan.logger.composition.LoggerSimpleComposition`

```Python
from propan.logger.composition import LoggerSimpleComposition, PriorityPair

logger = LoggerSimpleComposition([
    PriorityPair(logger=LoguruAdapter(), priority=1)
])
```
* В таком случае logger'ы будут применяться в порядке приоритета

Все logger'ы  поддерживают декоратор `logger.catch`, который позволяет совершать какие-либо действия при возникновении ошибки в функции

```Python
@logger.catch
@app.queue_handler(queue_name="test_queue")
async def base_handler(user: str):
    print(user)
```

### Дополнительно

Для возвращения сообщения в очередь при возникновении ошибки c отслеживанием количества попыток повторной обработки используйте декоратор `queue_adapter.retry_on_error`

```Python
@app.queue_adapter.retry_on_error(queue_name="test_queue", try_number=3)
@app.queue_handler(queue_name="test_queue")
async def base_handler(user: str):
    print(user)
```
* Замечания
    * При превышении количества повторных попыток `queue_adapter` вызывает метод `error` своего экземпляра `logger`'а, а сообщение извлекается из очереди
    * По умолчанию количество попыток - 3, название очереди - обязательный аргумент

В таком случае также может быть полезным использование декоратора `ignore_exceprions`

```Python
from propan.logger.utils import ignore_exceptions

NOT_CATCH = (ValueError,)

@app.queue_adapter.retry_on_error(queue_name="test_queue", try_number=3)
@app.queue_handler(queue_name="test_queue")
@ignore_exceptions(logger, NOT_CATCH)
async def base_handler(user: str):
    print(user)
```

* Ошибки из `NOT_CATCH` не будут передаваться дальше по стеку, а будут обработаны с помощью метода `error` переданного экземпляра `logger`'а


Худший вариант вашего приложения будет выглядеть следующим образом:

```Python
from propan.app import PropanApp
from propan.annotations.decorate import apply_types

from .dependencies import queue_adapter, logger


app = PropanApp(
    queue_adapter=queue_adapter,
    apply_types=True
)

NOT_CATCH = (ValueError,)


@logger.catch
@app.queue_adapter.retry_on_error(queue_name="test_queue", try_number=3)
@app.queue_handler(queue_name="test_queue")
@ignore_exceptions(logger, NOT_CATCH)
@apply_types
async def base_handler(user: str):
    print(user)
```

# Удачи!