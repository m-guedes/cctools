# List recipes.
default:
    @just --list

setup:
    uv sync --locked

# Read-only: lint, format and type checks.
lint:
    uv run --locked ruff check --no-fix .
    uv run --locked ruff format --check .
    uv run --locked mypy

# Apply lint fixes, then format.
fmt:
    uv run --locked ruff check --fix-only .
    uv run --locked ruff format .

install:
    uv tool install .

uninstall:
    uv tool uninstall cctools
