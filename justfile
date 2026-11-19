# List recipes.
default:
    @just --list

setup:
    uv sync

# Read-only: lint, format and type checks.
lint:
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy

# Apply lint fixes, then format.
fmt:
    uv run ruff check --fix-only .
    uv run ruff format .

# Extra arguments are forwarded to pytest.
test *args:
    uv run pytest --cov {{ args }}

install:
    uv tool install .

uninstall:
    uv tool uninstall cctools
