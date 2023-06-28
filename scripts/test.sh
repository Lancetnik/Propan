run_final_tests() {
    coverage run -m pytest -m "run" -k test_run_rabbit_correct tests/cli/test_run.py "$1" && \
    coverage run -m pytest -m "run" -k test_run_redis_correct tests/cli/test_run.py "$1" && \
    coverage run -m pytest -m "run" -k test_run_kafka_correct tests/cli/test_run.py "$1" && \
    coverage run -m pytest -m "run" -k test_run_nats_correct tests/cli/test_run.py "$1" && \
    coverage run -m pytest -m "run" -k test_run_sqs_correct tests/cli/test_run.py "$1"
}

(
    coverage run -m pytest -m "all and not run" "$@" || \
    coverage run -m pytest -m "all and not run" "$@"
) && run_final_tests "$@"