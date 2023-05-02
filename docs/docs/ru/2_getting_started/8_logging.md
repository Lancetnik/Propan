# LOGGING 

**Propan** использует для логирования 2 зараннее сконфигурированных логера:

* `propan` - используется PropanApp
* `propan.access` - используется брокером

## Логирование запросов

Для логирования запросов настоятельно рекомендуется использовать `access_logger` вашего брокера, т.к. он
доступен через [Context](../../5_dependency/2_context) вашего приложения.

```python
from propan import RabbitBroker
from propan.annotations import Logger

broker = RabbitBroker()

@broker.hanle("test")
async def func(logger: Logger):
    logger.info("message received")
```

Такой подход несет несколько преимуществ:

* используемый логер уже содержит контекс запроса: идентификатор сообщения, источник его получения
* заменив `logger` при инициализации вашего брокера вы автоматически замените все логеры внутри ваших функций

## Уровни логирования

Если вы используете **Propan CLI**, вы можете изменить текущий уровень логирования всего приложения прямо из командной строки.

Флаг `--log-level` устанавливает текущий уровень логирования как для брокера, так и для PropanApp. Так вы можете настраивать уровни не только дефолтных логеров, но и собственных, если используете их внутри **Propan**

<div class="termy">
```console
$ propan run serve:app --log-level debug
```
</div>

Если же вы хотите полностью отключить дефолтное логирование `Propan`, вы можете установить `logger=None`

```python
from propan import PropanApp, RabbitBroker

broker = RabbitBroker(logger=None)    # отключает логи broker'а
app = PropanApp(broker, logger=None)  # отключает логи приложения
```

!!! warning
    Будьте аккуратны: `logger`, который вы получаете из контекста также будет иметь значение `None`, если вы выключите логирование брокера

Если же вы не хотите терять доступ к `logger`'у внутри вашего контекста, но хотите избавиться от дефолтных логов **Propan**, вы можете понизить уровень логов, который публикует сам брокер.

```python
import logging
from propan import PropanApp, RabbitBroker

# устанавливает логи самого брокера на уровень DEBUG
broker = RabbitBroker(log_level=logging.DEBUG)
```

## Форматирование логов

Если вас не устраивает текущий формат логов вашего приложения, вы можете легко изменить его прямо в конструкторе вашего брокера

```python
from propan import PropanApp, RabbitBroker
broker = RabbitBroker(log_fmt="%(asctime)s %(levelname)s - %(message)s")
```

## Использование собственных логеров

Так как **Propan** работает со стандартным объектом `logging.Logger`, вы можете инициировать приложение и брокера
с помощью своего собственного логера

```python
import logging
from propan import PropanApp, RabbitBroker

logger = logging.getLogger("my_logger")

broker = RabbitBroker(logger=logger)
app = PropanApp(broker, logger=logger)
```

При этом вы потеряете информацию о контексте текущего запроса. Однако, вы можете получить ее напрямую из контекста в любом месте вашего кода:

```python
from propan import context
log_context: dict[str, str] = context.get_local("log_context")
```

## Доступ к logger

Если же вы хотите переопределить поведение дефолтных логеров, вы можете получить доступ к ним напрямую через `logging`:

```python
import logging
logger = logging.getLogger("propan")
access_logger = logging.getLogger("propan.access")
```
Или импортируя их из **Propan**

```python
from propan.log import access_logger, logger
```

