# Приведение типов

Первый аргумент функции, обрамленной в `@broker.hanle` - это расшифрованное тело входящего сообщения.

Тело входящих сообщений в **Propan** может быть одним из трех типов:

* `str` - если сообщение имеет заголовок `content-type: text/plain`
* `dict` - если сообщение имеет заголовок `content-type: application/json`
* `bytes` - если сообщение имеет любой другой заголовок

В качестве аннотации могут использоваться либо эти типы, либо любые примитивные типы, к которым **pydantic** сможет привести входящие аргументы (например `str -> float`).

Несколько примеров:

### text/plain

```python
@broker.handle("test")
async def base_handler(body: str):
    '''
    Мы ожидаем text/plain сообщение
    Сообщения другого вида спровоцируют ошибку
    '''

```

### application/json

```python
@broker.handle("test")
async def base_handler(body: dict):
    '''
    Мы ожидаем application/json сообщение
    Сообщения другого вида спровоцируют ошибку
    '''
```

### Any type

```python
@broker.handle("test")
async def base_handler(body: bytes):
    '''
    Мы ожидаем 'сырое' сообщение
    Сообщения другого вида спровоцируют ошибку
    '''
```

### Pydantic

Также, если вы используете в качестве аннотации типов объект `pydantic`, **Propan** также приведет входящее сообщение
к этому виду, если это возможно.

```python
from pydantic import BaseModel

class Message(BaseModel):
    key: float

@broker.handle("test")
async def base_handler(body: Message):
    '''
    Мы ожидаем application/json сообщение
    Вида { key: 1.0 }
    Сообщения другого вида спровоцируют ошибку
    '''
```

### Несколько аргументов

При аннотировании нескольких входящих аргументов, результат будет равносилен использованию использованию аналогичной `pydantic` модели.

```python
from pydantic import BaseModel

class Message(BaseModel):
    a: int
    b: float

@broker.handle("test")
async def base_handler(a: int, b: float):
# async def base_handler(body: Message): - аналогично
    '''
    Мы ожидаем application/json сообщение
    Вида { a: 1, b: 1.0 }
    Сообщения другого вида спровоцируют ошибку
    '''
```
