# Зависимости

**Propan** использует второстепенную библиотеку [**FastDepends**](https://lancetnik.github.io/FastDepends/){target="_blank"} ддя управления зависимостями.
Эта система зависимостей буквально позаимствована у **FastAPI**, так что, если вы умеет работать с этим фреймворков - вы умеете работать с зависимостями в Propan.

Вы можете перейти в документацию [**FastDepends**](https://lancetnik.github.io/FastDepends/){target="_blank"}, если хотите получить больше подробностей, однако, ключевые моменты и **дополнения** будут освещены здесь.

## Приведение типов

Ключевой функцией в системе управления зависимостями и приведения типов в *Propan* является декоратор `@apply_types` (@inject в FastDepends).

По умолчанию он применяется ко всем обработчикам событий, если только вы не отключили соответсвующую опцию при создании брокера.

=== "Redis"
    ```python
    from propan import RedisBroker
    broker = RedisBroker(..., apply_types=False)
    ```

=== "RabbitMQ"
    ```python
    from propan import RabbitBroker
    broker = RabbitBroker(..., apply_types=False)
    ```

=== "NATS"
    ```python
    from propan import NatsBroker
    broker = NatsBroker(..., apply_types=False)
    ```

!!! warning
    Выставив флаг `apply_types=False` вы отключаете не только приведение типов, но и `Depends`, `Context`.

Этот флаг может быть полезен, если вы используете **Propan** в рамках другого фреймворка и вам не нужно использовать
нативную систему зависимостей.

## Внедрение зависимостей

Для внедрения зависимостей в **Propan** используется специальный класс **Depends**

=== "Redis"
    ```python linenums="1" hl_lines="6-7"
    {!> docs_src/quickstart/dependencies/basic/1_propan_redis_depends.py !}
    ```

=== "RabbitMQ"
    ```python linenums="1" hl_lines="6-7"
    {!> docs_src/quickstart/dependencies/basic/1_propan_rabbit_depends.py !}
    ```

=== "NATS"
    ```python linenums="1" hl_lines="6-7"
    {!> docs_src/quickstart/dependencies/basic/1_propan_nats_depends.py !}
    ```

**Первым шагом**: нам нужно объявить зависимость - это может быть любой `Callable` объект.

??? note "Callable"
    "Callable" - объект, который может быть "вызван". Это может быть функция, класс или метод класса.

    Другими словами: если вы можете написать такой код `my_object()` - `my_object` будет `Callable`

=== "Redis"
    ```python hl_lines="1" linenums="10"
    {!> docs_src/quickstart/dependencies/basic/1_propan_redis_depends.py [ln:10-11]!}
    ```

=== "RabbitMQ"
    ```python hl_lines="1" linenums="10"
    {!> docs_src/quickstart/dependencies/basic/1_propan_rabbit_depends.py [ln:10-11]!}
    ```

=== "NATS"
    ```python hl_lines="1" linenums="10"
    {!> docs_src/quickstart/dependencies/basic/1_propan_nats_depends.py [ln:10-11]!}
    ```

**Вторым шагом**: объявите, какие зависимости вам нужны с помощью `Depends`

=== "Redis"
    ```python hl_lines="2" linenums="10"
    {!> docs_src/quickstart/dependencies/basic/1_propan_redis_depends.py [ln:10-11]!}
    ```

=== "RabbitMQ"
    ```python hl_lines="2" linenums="10"
    {!> docs_src/quickstart/dependencies/basic/1_propan_rabbit_depends.py [ln:10-11]!}
    ```

=== "NATS"
    ```python hl_lines="2" linenums="10"
    {!> docs_src/quickstart/dependencies/basic/1_propan_nats_depends.py [ln:10-11]!}
    ```

**Последним шагом**: просто используйте результат выполнения вашей зависимости!

Это ведь просто, разве нет?

!!! tip "Автоматическое применений @apply_types"
    В коде выше мы не использовали этот декоратор для наших зависимостей. Однако, он все равно применяется
    ко всем функциям, используемым в качестве зависимостей. Держите это в уме. 

## Вложенные зависимости

Зависимости также могут содержать другие зависимости. Это работает очень предсказуемым образом: просто объявите
`Depends` в зависимой функции.

=== "Redis"
    ```python linenums="1" hl_lines="6-7 9-10 15-16"
    {!> docs_src/quickstart/dependencies/basic/2_propan_redis_depends.py !}
    ```

    1. Здесь вызывается вложенная зависимость

=== "RabbitMQ"
    ```python linenums="1" hl_lines="6-7 9-10 15-16"
    {!> docs_src/quickstart/dependencies/basic/2_propan_rabbit_depends.py !}
    ```

    1. Здесь вызывается вложенная зависимость

=== "NATS"
    ```python linenums="1" hl_lines="6-7 9-10 15-16"
    {!> docs_src/quickstart/dependencies/basic/2_propan_nats_depends.py !}
    ```

    1. Здесь вызывается вложенная зависимость

!!! Tip "Кеширование"
    В примере выше функция `another_dependency` будет вызвана **ОДИН РАЗ!**.
    `Propan` кеширует все результаты выполнения зависимостей в рамках **ОДНОГО** `@apply_stack` стека вызова.
    Это означает, что все вложенные зависимости получат закешированный результат выполнения зависимости.
    Но, между разными вызовами основной функции, эти результаты будут различными.

    Чтобы предотвратить это поведение, просто используйте `Depends(..., cache=False)`. В этом случае зависимость будет испольняться для каждой функции
    в стеке вызова, где она используется.

## Использование с обычными функциями

Вы можете использовать декоратор `@apply_types` не только вместе с вашими `@broker.hanle`'ми, но и с обычными функциями: как синхронными, так и асинхронными.

=== "Sync"
    ```python hl_lines="3-4" linenums="1"
    {!> docs_src/quickstart/dependencies/basic/3_sync.py !}
    ```

=== "Async"
    ```python hl_lines="4-5 7-8" linenums="1"
    {!> docs_src/quickstart/dependencies/basic/3_async.py !}
    ```

    !!! tip "Будьте аккуратны"
        В асинхронном коде вы можете использовать как синхронные, так и асинхронные зависимости.
        Но в синхронном коде вам доступны только синхронные зависимости.

## Приведение типов зависимостей

**FastDepends**, используемый **Propan**, также приводит тип `return`. Это означает, что значение, возвращаемое зависимостью будет
дважды приводиться к типу: как `return` это зависимости и как входной аргумент основной функции. Это не несет дополнительных расходов, если
эти типы имеют одну и ту же аннотацию. Просто держите это в голове. Или нет... В любом случае, я вас предупредил.

```python linenums="1"
from propan import Depends, apply_types

def simple_dependency(a: int, b: int = 3) -> str:
    return a + b  # 'return' приводится к `str` в первый раз

@inject
def method(a: int, d: int = Depends(simple_dependency)):
    # 'd' приводится к `int` во второй раз
    return a + d

assert method("1") == 5
```

Также, результат выполнения зависимости кешируется. Если вы используете эту зависимости в `N` функциях,
этот закешированный результат будет приводится к типу `N` раз (на входе в используемую функцию).

Для избежания проблем с этим, используйте [mypy](https://www.mypy-lang.org){target="_blank"} или просто будьте аккуратны с аннотацией типов в вашем проекте.
