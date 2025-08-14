PYTHON := python
PIP := pip

.PHONY: install lint test run freeze

install:
	$(PIP) install -e .[dev]

lint:
	ruff check .
	black --check .
	isort --check-only .

test:
	pytest -q

run:
	$(PYTHON) -m dedart

freeze:
	$(PIP) freeze > requirements-lock.txt

