bash scripts/test.sh "$@"
coverage combine
coverage report --show-missing
coverage html

rm docs/files/coverage.svg
coverage-badge -o docs/files/coverage.svg

rm .coverage*