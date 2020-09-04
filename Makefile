install:
	pip install . -U

clean:
	rm -rf build dist docs/build pip-wheel-metadata .mypy_cache .pytest_cache
	find . -regex ".*/__pycache__" -exec rm -rf {} +
	find . -regex ".*\.egg-info" -exec rm -rf {} +
	pre-commit clean || true

legal:
	python tools/license_and_headers.py

lint:
	pre-commit run -a --hook-stage manual

test:
	pytest tests

install-test-requirements:
	pip install -r test_requirements.txt -U

install-pre-commit: install-test-requirements
	pre-commit install --install-hooks

uninstall-pre-commit:
	pre-commit uninstall
	pre-commit uninstall --hook-type pre-push

secret-scan:
	trufflehog --max_depth 1 .
