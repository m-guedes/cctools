.PHONY: setup
setup:
	@# A Python version is not explicitly specified via the --python flag because it is picked up from
	@# the special .python-version file.
	uv sync --dev

.PHONY: lint
lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src/

.PHONY: fmt
fmt:
	uv run ruff format .

.PHONY: test
test:
	uv run pytest tests/ --cov=src/ --cov-report=term-missing