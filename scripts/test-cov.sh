bash scripts/test.sh "$@"
coverage run -m pytest -m "run" -k test_run_nats_correct tests/cli/test_run.py
coverage run -m pytest -m "run" -k test_run_rabbit_correct tests/cli/test_run.py
coverage run -m pytest -m "run" -k test_run_kafka_correct tests/cli/test_run.py
coverage run -m pytest -m "run" -k test_run_sqs_correct tests/cli/test_run.py
coverage run -m pytest -m "run" -k test_run_redis_correct tests/cli/test_run.py

coverage combine
coverage report --show-missing

rm .coverage*