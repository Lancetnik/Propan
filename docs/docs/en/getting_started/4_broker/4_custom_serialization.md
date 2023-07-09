# Custom Serialization

By default, **Propan** uses the *JSON* format to send and receive messages. However, if you need to handle messages in other formats or with extra serialization steps such as *gzip*, *Avro*, *Protobuf*, and the like, you can modify the serialization logic.

## Serialization Steps

Before the message gets into your handler, **Propan** applies 2 functions to it sequentially: `parse_message` and `decode_message`. You can modify one or both stages depending on your needs.

### Message Parsing

At this stage, **Propan** serializes an incoming message of the framework that is used to work with the broker into a general view - **PropanMessage**. At this stage, the message body remains in the form of raw bytes.

The signature of the function looks like this:

{! includes/getting_started/broker/serialization/parse_signature.md !}

This stage is strongly related to the features of the broker used and in most cases, its redefinition is not necessary.

However, it is still possible. You can override this method both for the entire broker and for individual handlers:

```python linenums="1" hl_lines="3 6 8"
{!> docs_src/quickstart/broker/serialization/2_parse_redefine.py !}
```

Your function should take 2 arguments: a "raw" message itself and the original handler function. Thus, you can either completely redefine the message parsing logic, or partially modify a message, and then use the original **Propan** mechanism.

The parser declared at the `broker` level will be applied to all handlers. The parser declared at the `handle` level is applied only to this handler (it ignores the `broker' parser if it was specified earlier).

### Message Decoding

At this stage, the body of **PropanMessage** is transformed to the form in which it enters your handler function. This method you will have to redefine more often.

In the original, its signature is quite simple (this is a simplified version):

```python linenums="1"
{!> docs_src/quickstart/broker/serialization/3_decode.py !}
```

To redefine it, use the same way as the parser:

```python linenums="1" hl_lines="3 6 8"
{!> docs_src/quickstart/broker/serialization/4_decode_redefine.py !}
```

## Example with Protobuf

In this section, we will look at an example using *Protobuf*, however, it is also applicable for any other serialization methods.

???- note "Protobuf"
    *Protobuf* is an alternative message serialization method commonly used in *GRPC*. Its main advantage is much smaller [^1] message size (compared to *JSON*), but it requires a message schema (`.proto` files) both on the client side and on the server side.

To begin with, install the dependencies:

```console
pip install grpcio-tools
```

Then we will describe the scheme of our message

```proto title="message.proto"
syntax = "proto3";

message Person {
    string name = 1;
    float age = 2;
}
```

Now we will generate a *Python* class for working with messages in the *Protobuf format*

```console
python -m grpc_tools.protoc --python_out=. --pyi_out=. -I . message.proto
```

At the output, we get 2 files: `message_pb2.py` and `message_pb2.pyi`. Now we are ready to use the generated class to serialize our messages.

```python linenums="1" hl_lines="1 10-13 15 21"
{!> docs_src/quickstart/broker/serialization/5_protobuf.py !}
```

Note that we used the `NoCast` annotation, which excludes the message from the `pydantic` representation of our handler.

```python
{!> docs_src/quickstart/broker/serialization/5_protobuf.py [ln:16] !}
```

[^1]:
    For example, a message like `{ "name": "john", "age": 25 }` in *JSON* takes **27** bytes, and in *Protobuf* - **11**. With lists and more complex structures, the savings can be even more significant (up to 20x times).
