# CHANGELOG 

## **0.0.9** 2023-04-18

Релиз приурочен к выходу в свет другой библиотеки: [fast-depends](https://lancetnik.github.io/FastDepends/).
Теперь **Propan** используется ее в качестве системы управления зависимостями. `Context` также переосмыслен - теперь
это наследник *fast-depends CustomField*.

<h3>Особенности сборки:</h3>
* Вложенность `Depends`
* Более гибкое поведение `Context`
* Полностью протестированная и стабильная система управления зависимостями
* Добавлен модуль `propan.annotation` для быстрого доступа к уже существующим объектам контекста

<h3>Breaking changes:</h3>
* `@use_context` был удален. Используйте `@apply_types` для внедрения `Context`
* `Alias` был перемещен как часть `Context`
* Доступ к объектам контекста больше нельзя получить просто объявив аргумент функции

Теперь нужно использовать следующий код:
```python
from propan import Context, apply_types
@apply_types
def func(logger = Context()): ...

# or
from propan import Context, apply_types
@apply_types
def func(l = Context("logger")): ...

# or
from propan import apply_types
from propan.annotations import Logger
@apply_types
def func(logger: Logger): ...
```

---

## **INITIAL** 2023-04-05

Привет! Поздравляю всех и, особенно, себя с первым стабильным релизом *Propan*!

</h3>Особенности сборки</h3>
</h4>Стабильныe</h4>
* async RabbitMQ broker
* инъекция зависимостей
* преобразование типов
* инструмент CLI

<h4>Экспериментальные</h4>
В релиз добавлена первая реализация поддержки *NATS* (без использования Jetstream).

<h4>Следующие шаги</h4>
* Полная поддержка NATS
* Синхронная версия брокеров и приложения
* Разработка инструментов тестирования
