# Pattern

**Pattern** Channel is a powerful *Redis* routing engine. This type of `channel` sends messages to consumers by the *pattern*
specified when they connect to the `channel` and a message key.

## Scaling

If the message key matches the pattern of several consumers, it will be sent to **all** them.
Thus, horizontal scaling by increasing the number of consumer services is not possible only using *Redis Pub/Sub*.

If you need similar functionality, look towards *Redis Streams* or other brokers (for example, *Nats* or *RabbitMQ*).

## Example

```python linenums="1"
{!> docs_src/redis/pattern.py !}
```

### Consumer Announcement

To begin with, we have announced several consumers for two channels `*.info*` and `*.error`:

```python linenums="8" hl_lines="1 6 11"
{!> docs_src/redis/pattern.py [ln:8-20]!}
```

!!! note
    Note that `handler1` and `handler2` are subscribed to the same `channel`:
    both of these handlers will receive messages.

### Message distribution

Now the distribution of messages between these consumers will look like this:

```python
{!> docs_src/redis/pattern.py [ln:25]!}
```

The message `1` will be sent to `handler1` and `handler2` because they are listening to `channel` with the pattern `*.info*`

---

```python
{!> docs_src/redis/pattern.py [ln:26]!}
```

The message `2` will be sent to `handler3` because it listens to `channel` with the pattern `*.error`
