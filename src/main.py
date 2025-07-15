import argparse
import pprint
import sys
from parser import Parser

from error_handling import LexerError, ParserError
from lexer import tokenize_from_file


def main():
    parser = argparse.ArgumentParser(description="JSON lexer and parser")
    parser.add_argument("filename", help="Path to the JSON input file")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print tokens"
    )
    args = parser.parse_args()

    try:
        tokens = tokenize_from_file(args.filename)

        if args.verbose:
            for token in tokens:
                print(token)

        parser_instance = Parser(tokens)
        output = parser_instance.parse_value()

        pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)
        pp.pprint(output)

    except (LexerError, ParserError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
