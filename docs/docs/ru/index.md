<p align="center">
    <img src="assets/img/logo-no-background.png" alt="Propan logo" style="height: 250px; width: 600px;"/>
</p>

<p align="center">
    <a href="https://github.com/Lancetnik/Propan/actions/workflows/tests.yml" target="_blank">
        <img src="https://github.com/Lancetnik/Propan/actions/workflows/tests.yml/badge.svg" alt="Tests coverage"/>
    </a>
    <a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/lancetnik/propan" target="_blank">
        <img src="https://coverage-badge.samuelcolvin.workers.dev/lancetnik/propan.svg" alt="Coverage">
    </a>
    <a href="https://pypi.org/project/propan" target="_blank">
        <img src="https://img.shields.io/pypi/v/propan?label=pypi%20package" alt="Package version">
    </a>
    <a href="https://pepy.tech/project/propan" target="_blank">
        <img src="https://static.pepy.tech/personalized-badge/propan?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads" alt="downloads"/>
    </a>
    <br/>
    <a href="https://pypi.org/project/propan" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/propan.svg" alt="Supported Python versions">
    </a>
    <a href="https://github.com/Lancetnik/Propan/blob/main/LICENSE" target="_blank">
        <img alt="GitHub" src="https://img.shields.io/github/license/Lancetnik/Propan?color=%23007ec6">
    </a>
</p>

# Propan

**Propan** - это современный высокопроизводительный фреймоворк для построения приложений в соответсвии с <a href="https://microservices.io/patterns/communication-style/messaging.html" target="_blank">Messaging Architecture</a>.

**Propan** - высокоуровневый фреймворк, он разработан на основе популярных *python* библиотек для работы со специфичными брокерами, а в его основе лежит [*pydantic*](https://docs.pydantic.dev/) и идеи [*fastapi*](https://fastapi.tiangolo.com/ru/), [*pytest*](https://docs.pytest.org/en/7.3.x/).


!!! warning "В разработке"
    Основные концепции уже заложены, большая часть фич реализована, а тестов - написано. Однако, изменения, нарушающие обратную совместимость, все еще возможны до выхода версии **0.1.0**. Такие изменения будут отражены в [CHANGELOG](https://lancetnik.github.io/Propan/CHANGELOG/), поэтому следите за обновлениями.

---

## Ключевые особенности

* **Простота**: спроектирован для максимальной простоты изучения и использования.
* **Интуитивность**: Отличная поддержка IDE, автодополнение даже в *vim*`е.
* [**Управление зависимостями**](#dependencies): Эффективное переиспользование за счет аннотации типов. Доступ к зависимостями во всем стеке вызова.
* [**Интeграция**](#http-frameworks-integrations): Propan полностью совместим с [любыми http фреймворками](https://lancetnik.github.io/Propan/integrations/integrations-index/)
* **Независимость от брокеров**: Единый интерфейс для популярных брокеров:
    * **NATS** (основан на [nats-py](https://github.com/nats-io/nats.py)) 
    * **RabbitMQ** (основан на [aio-pika](https://aio-pika.readthedocs.io/en/latest/)) 
* [**Скорость разработки**](#cli-power): собственный *cli* инструмент предоставляет отличный опыт разработки:
    * Полностью совместимый с вашим фреймворком способ управлять окружением проекта
    * *hotreloading* при изменениях в коде (мне этого не хватало)
    * Готовые шаблоны проекта

---

## О фреймворке

*Python* богат на http-фреймворки, однако, если вы планируете активно работать с брокерами сообщений, ваш инструментарий резко сужается, а удобство и скорость разработки - падают.

Традиционные библиотеки для работы с популярными брокерами: *Kafka*, *RabbitMQ*, *Nats* и другими имеют далеко не самые удобные интерфейсы, к которым привыкло большинство веб разработчиков.

Кроме этого, они требуют глубокого погружения в нюансы архитектуры выбранного брокера, даже если вы хотите "просто попробовать".

**Propan** призван исправить эти досадные упущения: фреймворк предоставляет унифицированный интерфейс для работы с различными брокерами сообщений, который будет привычен большинству *python* разработчиков.

В простейшем случае фреймворк избавит вас от необходимости тратить время на изучение особенностей выбранного брокера: *Hello, World!* сможет написть любой школьник.

Для более искушенных разработчиков **Propan** оставляет возможность использовать все особенности выбранного брокера, оставаясь открытым для расширения на самом низком уровне. Также **Propan** предоставляет минимальный необходимый набор для удобства разработки: полная поддержка аннотации типов и автодополнений, hotreloading, управление окружением приложения через *cli*, а также поставка готовых шаблонов приложений.

## Поддерживаемые брокеры

!!! note "Нужна ваша помощь"
    Фреймоворк сейчас активно развивается и расширяется. У нас очень длинный список того, что еще предстоит реализовать и различные брокеры - только его часть. Если вы хотите реализовать что-то из этого списка или помочь любым другим способом - загляните [сюда](https://lancetnik.github.io/Propan/contributing/contributing-index/)

|              | async                                                   | sync                 |
|--------------|:-------------------------------------------------------:|:--------------------:|
| **RabbitMQ** | :heavy_check_mark: **stable** :heavy_check_mark:        | :mag: planning :mag: |
| **Nats**     | :warning: **beta** :warning:                            | :mag: planning :mag: |
| **NatsJS**   | :hammer_and_wrench: **in progress** :hammer_and_wrench: | :mag: planning :mag: |
| **MQTT**     | :mag: planning :mag:                                    | :mag: planning :mag: |
| **REDIS**    | :mag: planning :mag:                                    | :mag: planning :mag: |
| **Kafka**    | :mag: planning :mag:                                    | :mag: planning :mag: |
| **SQS**      | :mag: planning :mag:                                    | :mag: planning :mag: |

