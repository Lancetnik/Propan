# TODO

The project is currently under active development and I really need your help to bring it to release as soon as possible!

## Documentation

At the moment, the main activity for the development of the project is the preparation of documentation.

You will be very helpful if

* Correct errors, typos, inaccuracies
* Edit or supplement individual sections where something is not described clearly enough
* Add translations of individual pages or sections

To participate in the development of documentation, go to the following [section] (/Propan/7_contributing/3_docs/)

## Code

If you want to work a little with the code, then you have even more opportunities to prove yourself. At the moment, the priority of the project is the following tasks:

* `PushBackWatcher` should store information about the number of message processing in the header:
this will allow you to keep a common counter for all consumers.
* Implement sending an RPC response via the `return` function of the event handler
* Merge the arguments of the methods `__init__` and `connect` brokers for more flexible management of default values
* Coverage with `NatsBroker` tests
* Implementation of `NatsJSBroker`
* Implementation of the synchronous version of the application and brokers
* Broker implementation for `Apache Kafka' and other brokers from [plan](/Propan/#_3)

To start developing the project, go to the following [section] (/Propan/7_contributing/2_contributing-index/).

If you want to develop your own adapter for any broker, you will find a lot of useful information in [this](/Propan/7_contributing/4_adapters/) section.