# JSON Parser

A JSON parser implementation in Python with excellent error reporting.

## Features

- Complete JSON support (objects, arrays, strings, numbers, booleans, null)
- Excellent error messages with line/column positions
- Unicode and escape sequence support
- Comprehensive test suite

## Development

This project uses Nix for dependency management.

```bash
# Enter development environment
nix develop

# Run tests
pytest tests/

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Usage

```bash
# Parse JSON from file
python -m src.main examples/simple.json

# Parse JSON from stdin
echo '{"hello": "world"}' | python -m src.main -
```

## Project Structure

- `src/` - Source code
  - `lexer.py` - Tokenizer
  - `parser.py` - Parser logic
  - `errors.py` - Error handling
  - `main.py` - CLI interface
- `tests/` - Test files
- `examples/` - Example JSON files
