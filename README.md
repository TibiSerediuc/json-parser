# JSON Parser

A JSON parser implementation in Python with excellent error reporting.

## Features

- Complete JSON support (objects, arrays, strings, numbers, booleans, null)
- Excellent error messages with line/column positions
- Unicode and escape sequence support
- Comprehensive test suite

## Development

This project uses Nix for system dependencies and UV for Python package management.

### Setup

```bash
# Enter development environment (creates and activates .venv automatically)
nix develop

# Install development dependencies
uv pip install -e ".[dev]"
```

### Development Commands

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Format code
uv run black .
uv run isort .

# Lint code
uv run flake8 src/ tests/

# Type checking
uv run mypy src/

# Run all checks
uv run pytest && uv run black . && uv run isort . && uv run flake8 . && uv run mypy src/
```

## Usage

```bash
# Parse JSON from file
uv run python -m src.main examples/simple.json

# Parse JSON from stdin
echo '{"hello": "world"}' | uv run python -m src.main -

# Or install and use directly
uv pip install -e .
json-parser examples/simple.json
```

## Project Structure

- `src/` - Source code
  - `lexer.py` - Tokenizer
  - `parser.py` - Parser logic
  - `errors.py` - Error handling
  - `main.py` - CLI interface
- `tests/` - Test files
- `examples/` - Example JSON files

## Development Workflow

1. Make changes to code
2. Run tests: `uv run pytest`
3. Format code: `uv run black . && uv run isort .`
4. Check types: `uv run mypy src/`
5. Lint: `uv run flake8 .`
