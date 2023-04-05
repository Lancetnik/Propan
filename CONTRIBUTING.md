## Developing

If you already cloned the repository and you know that you need to deep dive in the code, here are some guidelines to set up your environment.

### Virtual environment with `venv`

You can create a virtual environment in a directory using Python's `venv` module:

```bash
$ python -m venv venv
```

That will create a directory `./venv/` with the Python binaries and then you will be able to install packages for that isolated environment.

### Activate the environment

Activate the new environment with:

```bash
$ source ./venv/bin/activate
```

Make sure you have the latest pip version on your virtual environment to 
```bash
$ python -m pip install --upgrade pip
```

### pip

After activating the environment as described above:

```bash
$ pip install -e ."[dev]"
```

It will install all the dependencies and your local Propan in your local environment.

#### Using your local Propan

If you create a Python file that imports and uses Propan, and run it with the Python from your local environment, it will use your local Propan source code.

And if you update that local Propan source code, as it is installed with `-e`, when you run that Python file again, it will use the fresh version of Propan you just edited.

That way, you don't have to "install" your local version to be able to test every change.

To use your local Propan cli type:
```bash
$ python -m propan ...
```

### Tests

To run tests with your current Propan application and Python environment use:
```bash
$ bash ./scripts/test-cov.sh
```

To run all tests based on RabbitMQ, NATS or another dependencies you should run first following *docker-compose.yml*

```yaml
version: "3"

services:
  rabbit:
    image: rabbitmq
    ports:
      - 5672:5672
  
  nats:
    image: nats
    ports:
      - 4222:4222
```

```bash
$ docker compose up -d
```