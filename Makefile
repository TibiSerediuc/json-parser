.PHONY: help install test format lint typecheck clean all

help:
	@echo "Available commands:"
	@echo "  install    - Install project in development mode"
	@echo "  test       - Run tests"
	@echo "  format     - Format code with black and isort"
	@echo "  lint       - Lint code with flake8"
	@echo "  typecheck  - Type check with mypy"
	@echo "  clean      - Remove cache files"
	@echo "  all        - Run all checks (test, format, lint, typecheck)"

install:
	uv pip install -e ".[dev]"

test:
	uv run pytest

test-cov:
	uv run pytest --cov=src --cov-report=html --cov-report=term

format:
	uv run black .
	uv run isort .

lint:
	uv run flake8 src/ tests/

typecheck:
	uv run mypy src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov/

all: test format lint typecheck
	@echo "✅ All checks passed!"
