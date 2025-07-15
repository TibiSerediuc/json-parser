import os
from enum import Enum

from error_handling import LexerError


# Token vocabulary for JSON
class TokenType(Enum):
    NONE = None
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    COLON = ":"
    COMMA = ","
    STRING = "STRING"
    NUMBER = "NUMBER"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    EOF = "EOF"


# States for the machine state
class State(Enum):
    DEFAULT = 0
    STRING = 1
    NUMBER = 2
    LITERAL = 3
    ESCAPE = 4
    UNICODE_ESCAPE = 5


# Constants for lexer logic
SINGLE_CHAR_TOKENS = {
    TokenType.LEFT_BRACE.value,
    TokenType.RIGHT_BRACE.value,
    TokenType.LEFT_BRACKET.value,
    TokenType.RIGHT_BRACKET.value,
    TokenType.COLON.value,
    TokenType.COMMA.value,
}

# Maps the escape sequence characters
ESCAPE_MAP = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}

NUMBERS_VALID_CHARS = "-+0123456789eE."
LITERAL_STARTERS = "tfn"  # true, false, null
HEX_DIGITS = "0123456789ABCDEF"


class Token:
    """Represents a lexical token with type and value"""

    def __init__(self, _type: TokenType, value, position: int = 0):
        self.type = _type
        self.value = value
        self.position = position

    def __repr__(self):
        if self.value is None:
            self.value = str(None)
        return f"{self.type:<25} {self.value:<40}, pos={self.position:<5}"

    # Operator overload for '=='
    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value


class EscapeHandler:
    """Handles the escape sequence processing"""

    @staticmethod
    def process_escape(char: str) -> str:
        """Processes a single escape character"""
        if char in ESCAPE_MAP:
            return ESCAPE_MAP[char]
        raise LexerError(f"Invalid escape character '{char}'")

    @staticmethod
    def process_unicode_escape(hex_digits: str) -> str:
        """Processes Unicode escape sequence \\uXXXX"""
        if len(hex_digits) != 4:
            raise LexerError(
                "Invalid Unicode escape sequence " f"'\\u{hex_digits}'"
            )

        try:
            return chr(int(hex_digits, 16))
        except ValueError:
            raise LexerError(
                f"Invalid Unicode escape sequence '\\u{hex_digits}'"
            )

    @staticmethod
    def is_valid_hex_digit(char: str) -> bool:
        """Check if character is a valid hexadecimal digit"""
        return char in HEX_DIGITS


class NumberProcessor:
    """Handles number parsing and validation"""

    @staticmethod
    def is_valid_number_char(char: str) -> bool:
        """Check if the character is valid in a number"""
        return char in NUMBERS_VALID_CHARS

    @staticmethod
    def parse_number(buffer: str) -> bool:
        """Parse number string into int or float"""
        try:
            if "." in buffer or "e" in buffer.lower():
                return float(buffer)
            else:
                return int(buffer)
        except ValueError:
            raise LexerError(f"Invalid number format '{buffer}'")


class LiteralProcessor:
    """Handles literal parsing and validation (true, false, null)"""

    @staticmethod
    def process_literal(input_string: str, index: int) -> tuple[Token, int]:
        """Processes literal values, returns token and advances the index"""
        if input_string.startswith("true", index):
            return Token(TokenType.TRUE, True, index), index + 4
        elif input_string.startswith("false", index):
            return Token(TokenType.FALSE, False, index), index + 5
        elif input_string.startswith("null", index):
            return Token(TokenType.NULL, None, index), index + 4
        else:
            raise LexerError("Invalid literal", index)


class JSONLexer:
    """Main lexer class that tokenizes JSON strings"""

    def __init__(self, input_string: str):
        self.input_string = input_string
        self.index = 0
        self.state = State.DEFAULT
        self.buffer = ""
        self.unicode_buffer = ""
        self.tokens: list[Token] = []

    def current_char(self) -> str:
        """Get the current character"""
        if self.index >= len(self.input_string):
            return ""
        return self.input_string[self.index]

    def advance(self):
        """Advance to next character"""
        self.index += 1

    def add_token(self, token_type: TokenType, value):
        """Adds a token to the token list"""
        token = Token(token_type, value, self.index)
        self.tokens.append(token)

    def handle_single_char_token(self, char: str):
        """Handle single character tokens"""
        token_map = {
            "{": TokenType.LEFT_BRACE,
            "}": TokenType.RIGHT_BRACE,
            "[": TokenType.LEFT_BRACKET,
            "]": TokenType.RIGHT_BRACKET,
            ":": TokenType.COLON,
            ",": TokenType.COMMA,
        }
        self.add_token(token_map[char], char)

    def handle_default_state(self, char: str):
        """Handle the DEFAULT state logic"""
        if char.isspace():
            return

        self.buffer = ""
        if char in SINGLE_CHAR_TOKENS:
            self.handle_single_char_token(char)
        elif char == '"':
            self.state = State.STRING
        elif char == "-" or char.isdigit():
            self.buffer = char
            self.state = State.NUMBER
        elif char in LITERAL_STARTERS:
            self.state = State.LITERAL
            self.index -= 1  # we iterate in function handler
        else:
            raise LexerError(f"Unexpected character '{char}'", self.index)

    def handle_string_state(self, char: str):
        """Handle STRING state logic"""
        if char == "\\":
            self.state = State.ESCAPE
        elif char == '"':
            self.add_token(TokenType.STRING, self.buffer)
            self.state = State.DEFAULT
        else:
            self.buffer += char

    def handle_escape_state(self, char: str):
        """Handle ESCAPE state logic"""
        if char == "u":
            self.unicode_buffer = ""
            self.state = State.UNICODE_ESCAPE
        else:
            escaped_char = EscapeHandler.process_escape(char)
            self.buffer += escaped_char
            self.state = State.STRING

    def handle_unicode_escape_state(self, char: str):
        """Handle UNICODE_ESCAPE state logic"""
        if EscapeHandler.is_valid_hex_digit(char):
            self.unicode_buffer += char
            if len(self.unicode_buffer) == 4:
                unicode_char = EscapeHandler.process_unicode_escape(
                    self.unicode_buffer
                )
                self.buffer += unicode_char
                self.state = State.STRING
        else:
            raise LexerError(
                "Invalid Unicode escape sequence"
                f"'\\u{self.unicode_buffer}{char}'",
                self.index,
            )

    def handle_number_state(self, char: str):
        """Handle NUMBER state logic"""
        if NumberProcessor.is_valid_number_char(char):
            self.buffer += char
        else:
            value = NumberProcessor.parse_number(self.buffer)
            self.add_token(TokenType.NUMBER, value)
            self.state = State.DEFAULT
            self.buffer = ""
            self.index -= 1

    def handle_literal_state(self):
        """Handle LITERAL state logic"""
        token, new_index = LiteralProcessor.process_literal(
            self.input_string, self.index
        )
        self.tokens.append(token)
        self.index = new_index - 1
        self.state = State.DEFAULT

    def handle_end_of_input(self):
        """Handle any remaining state at the end of input"""
        if self.state == State.NUMBER:
            value = NumberProcessor.parse_number(self.buffer)
            self.add_token(TokenType.NUMBER, value)
        elif self.state == State.STRING:
            raise LexerError("Unterminated string", len(self.input_string))
        elif self.state == State.LITERAL:
            raise LexerError(
                f"Incomplete literal '{self.buffer}'",
                len(self.input_string) - len(self.buffer),
            )
        elif self.state == State.ESCAPE:
            raise LexerError(
                "Incomplete escape sequence", len(self.input_string)
            )
        elif self.state == State.UNICODE_ESCAPE:
            raise LexerError(
                "Incomplete UNICODE escaoe sequence "
                f"'\\u{self.unicode_buffer}'",
                len(self.input_string),
            )

    def tokenize(self) -> list[Token]:
        """Main tokenization method"""

        while self.index < len(self.input_string):
            char = self.current_char()

            if self.state == State.DEFAULT:
                self.handle_default_state(char)
            elif self.state == State.STRING:
                self.handle_string_state(char)
            elif self.state == State.ESCAPE:
                self.handle_escape_state(char)
            elif self.state == State.UNICODE_ESCAPE:
                self.handle_unicode_escape_state(char)
            elif self.state == State.NUMBER:
                self.handle_number_state(char)
            elif self.state == State.LITERAL:
                self.handle_literal_state()

            self.advance()

        self.handle_end_of_input()
        self.add_token(TokenType.EOF, None)
        return self.tokens


def tokenize_from_string(json_string: str) -> list[Token]:
    """
    Tokenize JSON from a string.

    Args:
        json_string (str): JSON string to tokenize

    Returns:
        List[Token] : list of tokens

    Raises:
        LexerError: If there's an error during tokenization
    """
    lexer = JSONLexer(json_string)
    return lexer.tokenize()


def tokenize_from_file(file_path: str) -> list[Token]:
    """
    Tokenize JSON from a file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        List[Token]: List of tokens

    Raises:
        FileNotFoundError: If the file doesn't exist
        LexerError: If there's an error during tokenization
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return tokenize_from_string(content)
    except IOError as e:
        raise LexerError(f"Error reading file '{file_path}': {e}", 0)
