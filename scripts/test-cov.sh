bash scripts/test.sh "$@"
coverage combine
coverage report --show-missing
coverage html