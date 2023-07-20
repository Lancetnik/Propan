# Developing

If you already cloned the repository and you know that you need to deep dive in the code, here are some guidelines to set up your environment.

### Virtual environment with `venv`

You can create a virtual environment in a directory using Python's `venv` module:

```bash
python -m venv venv
```

That will create a directory `./venv/` with the Python binaries and then you will be able to install packages for that isolated environment.

### Activate the environment

Activate the new environment with:

```bash
source ./venv/bin/activate
```

Make sure you have the latest pip version on your virtual environment to

```bash
python -m pip install --upgrade pip
```

### pip

After activating the environment as described above:

```bash
pip install -e ".[dev]"
```

It will install all the dependencies and your local Propan in your local environment.

#### Using your local Propan

If you create a Python file that imports and uses Propan, and run it with the Python from your local environment, it will use your local Propan source code.

And if you update that local Propan source code, as it is installed with `-e`, when you run that Python file again, it will use the fresh version of Propan you just edited.

That way, you don't have to "install" your local version to be able to test every change.

To use your local **Propan CLI** type:

```bash
python -m propan ...
```

### Tests

#### Pytest

To run tests with your current Propan application and Python environment use:

```bash
pytest tests
# or
bash ./scripts/test.sh
# with coverage output
bash ./scripts/test-cov.sh
```

There are some *pytest marks* at project:

* **slow**
* **rabbit**
* **nats**
* **sqs**
* **kafka**
* **redis**
* **all**

Default *pytest* calling runs "not slow" tests.

To run all tests use:

```bash
pytest -m 'all'
```

Also if you didn't up local rabbit or nats intance, run tests without that dependencies

```bash
pytest -m 'not rabbit and not nats'
```

To run all tests based on RabbitMQ, NATS or another dependencies you should run first following *docker-compose.yml*

```yaml
{! includes/docker-compose.yml !}
```

```bash
docker compose up -d
```

#### Hatch

If you are using **hatch** use following environments to run tests:

##### **TEST**

Run tests at all python 3.7-3.11 versions.

All python versions should be avalilable at your system.

```bash
# Run fast smoketesting at all python 3.7-3.11 versions
hatch run test:run

# Run all tests at all python versions
hatch run test:run-all
```

##### **TEST-LAST**

Run tests at python 3.11 version.

```bash
# Run smoke tests at python 3.11
hatch run test-last:run

# Run all tests at python 3.11
hatch run test-last:run-all

# Run all tests at python 3.11 and show coverage
hatch run test-last:cov
```
