# Pattern

**Pattern** Subject is a powerful *NATS* routing engine. This type of `subject` messages to consumers by the *pattern* specified when they connect to `subject` and a message key.

## Scaling

If one `subject` is listening by several consumers with the same `queue group`, the message will go to a random consumer each time.

Thus, *NATS* can independently balance the load on queue consumers. You can increase the processing speed of the message flow from the queue by simply launching additional instances of the consumer service. You don't need to make changes to the current infrastructure configuration: *NATS* will take care of how to distribute messages between your services.

## Example

```python linenums="1"
{!> docs_src/nats/pattern.py !}
```

### Consumer Announcement

To begin with, we have announced several consumers for two `subjects`: `*.info` and `*.error`:

```python linenums="7" hl_lines="1 5 9"
{!> docs_src/nats/pattern.py [ln:7-17]!}
```

At the same time, in the `subject` of our consumers, we specify the *pattern* that will be processed by these consumers.

!!! note
    Note that all consumers are subscribed using the same `queue_group`: within the same service, this does not make sense, since messages will come to these handlers in turn.
    Here we emulate the work of several consumers and load balancing between them.

### Message distribution

Now the distribution of messages between these consumers will look like this:

```python
{!> docs_src/nats/pattern.py [ln:21]!}
```

The message `1` will be sent to `handler1` or `handler2`, because they listen to the same `subject` template within the same `queue group`

---

```python
{!> docs_src/nats/pattern.py [ln:22]!}
```

Message `2` will be sent similarly to message `1`

---

```python
{!> docs_src/nats/pattern.py [ln:23]!}
```

The message `3` will be sent to `handler3`, because it is the only one listening to the pattern `*.error*`
