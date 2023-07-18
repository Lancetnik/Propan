# Type casting

The first argument of the function decorated by `@broker.handle` is the decrypted body of the incoming message.

Incoming message body can be of three types:

* `str` - if the message has the header `content-type: text/plain`
* `dict` - if the message has the header `content-type: application/json`
* `bytes` - if the message has any other header

Either these types can be used as an annotation, or any primitive types to which **pydantic** can cast incoming arguments (for example, `str -> float`).

A few examples:

### text/plain

```python
@broker.handle("test")
async def base_handler(body: str):
    '''
    We are expecting a text/plain message
    Messages of a different kind will raise an error
    '''

```

### application/json

```python
@broker.handle("test")
async def base_handler(body: dict):
    '''
    We are expecting an application/json message
    Messages of a different kind will raise an error
    '''
```

### Any type

```python
@broker.handle("test")
async def base_handler(body: bytes):
    '''
    We are expecting a 'raw' message
    Messages of a different kind will raise an error
    '''
```

### Pydantic

Also, if you use a `pydantic` object as the type annotation, **Propan** will also result in an incoming message of this kind, if possible:

```python
from pydantic import BaseModel

class Message(BaseModel):
    key: float

@broker.handle("test")
async def base_handler(body: Message):
    '''
    We are expecting an application/json message
    Type { key: 1.0 }
    Messages of a different kind will raise an error
    '''
```

### Multiple arguments

When annotating multiple incoming arguments, the result will be equivalent to using a similar `pydantic' model.

```python
from pydantic import BaseModel

class Message(BaseModel):
    a: int
    b: float

@broker.handle("test")
async def base_handler(a: int, b: float):
# async def base_handler(body: Message): - equivalent to using separate parameters
    '''
    We are expecting an application/json message
    Type { a: 1, b: 1.0 }
    Messages of a different kind will raise an error
    '''
```
