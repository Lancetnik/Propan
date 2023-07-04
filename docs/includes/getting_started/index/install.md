=== "Redis"
    <div class="termy">
    ```console
    $ pip install "propan[async-redis]"
    ---> 100%
    ```
    </div>
    !!! tip
        {{ run_docker }}
        ```bash
        docker run -d --rm -p 6379:6379 --name test-mq redis
        ```

=== "RabbitMQ"
    <div class="termy">
    ```console
    $ pip install "propan[async-rabbit]"
    ---> 100%
    ```
    </div>
    !!! tip
        {{ run_docker }}
        ```bash
        docker run -d --rm -p 5672:5672 --name test-mq rabbitmq
        ```

=== "Kafka"
    <div class="termy">
    ```console
    $ pip install "propan[async-kafka]"
    ---> 100%
    ```
    </div>
    !!! tip
        {{ run_docker }}
        ```bash
        docker run -d --rm -p 9092:9092 --name test-mq \
        -e KAFKA_ENABLE_KRAFT=yes \
        -e KAFKA_CFG_NODE_ID=1 \
        -e KAFKA_CFG_PROCESS_ROLES=broker,controller \
        -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
        -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
        -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
        -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://127.0.0.1:9092 \
        -e KAFKA_BROKER_ID=1 \
        -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@kafka:9093 \
        -e ALLOW_PLAINTEXT_LISTENER=yes \
        bitnami/kafka
        ```

=== "SQS"
    <div class="termy">
    ```console
    $ pip install "propan[async-sqs]"
    ---> 100%
    ```
    </div>
    !!! tip
        {{ run_docker }}
        ```bash
        docker run -d --rm -p 9324:9324 --name test-mq softwaremill/elasticmq-native
        ```

=== "NATS"
    <div class="termy">
    ```console
    $ pip install "propan[async-nats]"
    ---> 100%
    ```
    </div>
    !!! tip
        {{ run_docker }}
        ```bash
        docker run -d --rm -p 4222:4222 --name test-mq nats -js
        ```