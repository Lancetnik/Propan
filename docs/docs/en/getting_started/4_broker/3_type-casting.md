# Type casting

The first argument of the function decorated by `@broker.hanle` is the decrypted body of the incoming message.

It can be of three types:

* `str` - if the message has the header `content-type: text/plain`
* `dict` - if the message has the header `content-type: application/json`
* `bytes` - if the message has any other header

All incoming messages will be automatically brought to this view.

A few examples:

### text/plain

```python
@broker.handle("test")
async def base_handler(body: str):
    '''
    We are expecting a text/plain message
    Messages of a different kind will trigger an error
    '''

```

### application/json

```python
@broker.handle("test")
async def base_handler(body: dict):
    '''
    We are expecting an application/json message
    Messages of a different kind will trigger an error
    '''
```

### Any type

```python
@broker.handle("test")
async def base_handler(body: bytes):
    '''
    We are expecting a 'raw' message
    Messages of a different kind will trigger an error
    '''
```

### Pydantic

Also, if you use the `pydantic` object as a type annotation, **Propan** will also result in an incoming message
to this kind, if possible.

```python
from pydantic import BaseModel

class Message(BaseModel):
    key: float

@broker.handle("test")
async def base_handler(body: Message):
    '''
    We are expecting an application/json message
    Type { key: 1.0 }
    Messages of a different kind will trigger an error
    '''
```