# Direct

**Direct** Channel is the basic way to route messages in *Redis*. Its core is very simple: `channel` sends messages to all consumers subscribed to it.

## Scaling

If one channel is listening by several consumers, the message will be received by **all** consumers of this channel.
Thus, horizontal scaling by increasing the number of consumer services is not possible only using *Redis Pub/Sub*.

If you need similar functionality, look for *Redis Streams* or other brokers (for example, *Nats* or *RabbitMQ*).

## Example

**Direct** Channel is the default type used in **Propan**: you can simply declare it as follows

```python
@broker.handler("test_channel")
async def handler():
    ...
```

Full example:

```python linenums="1"
{!> docs_src/redis/direct.py !}
```

### Consumer Announcement

To begin with, we have announced several consumers for the two channels `test` and `test2`:

```python linenums="8" hl_lines="1 6 11"
{!> docs_src/redis/direct.py [ln:8-20]!}
```

!!! note
    Note that `handler1` and `handler2` are subscribed to the same `channel`:
    both of these handlers will receive messages.

### Message distribution

Now the distribution of messages between these consumers will look like this:

```python
{!> docs_src/redis/direct.py [ln:25]!}
```

The message `1` will be sent to `handler1` and `handler2` because they are listening to `channel` with the name `test`

---

```python
{!> docs_src/redis/direct.py [ln:26]!}
```

The message `2` will be sent to `handler3` because it listens to `channel` with the name `test2`