# Topic Exchange

**Topic** Exchange is a powerful *RabbitMQ* routing tool. This type of `exchange` sends messages to the queue in accordance with the *pattern* specified when they are connected to `exchange` and the `routing_key` of the message itself.

At the same time, if the queue listens to several consumers, messages will also be distributed among them.

## Example

```python linenums="1"
{!> docs_src/rabbit/topic.py !}
```

### Consumer Announcement

To begin with, we announced our **Topic** exchange and several queues that will listen to it:

```python linenums="8" hl_lines="1 3-4"
{!> docs_src/rabbit/topic.py [ln:8-11]!}
```

At the same time, in the `routing_key` of our queues, we specify the *pattern* of routing keys that will be processed by this queue.

Then we signed up several consumers using the advertised queues to the `exchange` we created

```python linenums="13" hl_lines="1 5 9"
{!> docs_src/rabbit/topic.py [ln:13-23]!}
```

!!! note
    `handler1` and `handler2` are subscribed to the same `exchange` using the same queue:
    within a single service, this does not make a sense, since messages will come to these handlers in turn.
    Here we emulate the work of several consumers and load balancing between them.

### Message distribution

Now the distribution of messages between these consumers will look like this:

```python
{!> docs_src/rabbit/topic.py [ln:27]!}
```

Messages `1` will be sent to `handler1` because it listens to `exchange` using a queue with the routing key `*.info`

---

```python
{!> docs_src/rabbit/topic.py [ln:28]!}
```

Messages `2` will be sent to `handler2` because it listens to `exchange` using the same queue, but `handler1` is busy

---

```python
{!> docs_src/rabbit/topic.py [ln:29]!}
```

Messages `3` will be sent to `handler1` again, because it is currently free

---

```python
{!> docs_src/rabbit/topic.py [ln:30]!}
```

Messages `4` will be sent to `handler3`, because it is the only one listening to `exchange` using a queue with the routing key `*.debug`