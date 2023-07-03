bash scripts/test.sh "$@"
coverage run -m pytest -m "run and rabbit" tests/cli/test_run.py
coverage run -m pytest -m "run and kafka" tests/cli/test_run.py
coverage run -m pytest -m "run and sqs" tests/cli/test_run.py
coverage run -m pytest -m "run and redis" tests/cli/test_run.py
coverage run -m pytest -m "run and nats" tests/cli/test_run.py

coverage combine
coverage report --show-missing

rm .coverage*