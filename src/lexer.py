import os
from enum import Enum
from error_handling import LexerError

# Token vocabulary for JSON
class TokenType(Enum):
    NONE = None
    LEFT_BRACE = '{'
    RIGHT_BRACE = '}'
    LEFT_BRACKET = '['
    RIGHT_BRACKET = ']'
    COLON = ':'
    COMMA = ','
    STRING = 'STRING'
    NUMBER = 'NUMBER'
    TRUE = 'true'
    FALSE = 'false'
    NULL = 'null'
    EOF = 'EOF'
    
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
        TokenType.COMMA.value
}

# Maps the escape sequence characters
ESCAPE_MAP = {
        '"' : '"',
        '\\': '\\',
        '/' : '/',
        'b' : '\b',
        'f' : '\f',
        'n' : '\n',
        'r' : '\r',
        't' : '\t'
}

NUMBERS_VALID_CHARS = "-+0123456789eE."
LITERAL_STARTERS = "tfn" # true, false, null
HEX_DIGITS = "0123456789ABCDEF"

class Token:
    """ Represents a lexical token with type and value """

    def __init__(self, _type: TokenType, value, position: int = 0):
        self.type = _type
        self.value = value
        self.position = position

    def __repr__(self):
        return f"{self.type}, {self.value}, pos={self.position}"

    # Operator overload for '=='
    def __eq__(self, other):
        if not instance(other, Token):
            return False
        return self.type == other.type and self.value == other.value

class EscapeHandler:
    """ Handles the escape sequence processing """

    def process_escape(char: str) -> str:
        """ Processes a single escape character """
        if char in ESCAPE_MAP:
            return ESCAPE_MAP[char]
        raise LexerError(f"Invalid escape character '{char}'")

    def process_unicode_escape(hex_digits: str) -> str:
        """ Processes Unicode escape sequence \\uXXXX """
        if len(hex_digits) != 4:
            raise LexerError(f"Invalid Unicode escape sequence '\\u{hex_digits}'")

        try:
            return chr(int(hex_digits, 16))
        except ValueError:
            raise LexerError(f"Invalid Unicode escape sequence '\\u{hex_digits}'")

    def is_valid_hex_digit(char: str) -> bool:
        """ Check if character is a valid hexadecimal digit """
        return char in HEX_DIGITS



def tokenize(input_string):
    """
    Main tokenizer function.

    Args:
        input_string (str): Input JSON string to be tokenized

    Returns:
        list: List of tokens

    Raises:
        LexerError: If there's an error during tokenization
    """

    state = State.DEFAULT
    index = 0
    tokens = []
    buffer = ''
    unicode_buffer = ''
    
    while index < len(input_string):
        currChar = input_string[index]
        
        if state == State.DEFAULT:
            if currChar.isspace():
                index += 1
                continue

            buffer = ''
    
            match currChar:
                case '{':                
                    tokens.append(Token(TokenType.LEFT_BRACE, currChar))

                case '}':
                    tokens.append(Token(TokenType.RIGHT_BRACE, currChar))

                case '[':
                    tokens.append(Token(TokenType.LEFT_BRACKET, currChar))

                case ']':
                    tokens.append(Token(TokenType.RIGHT_BRACKET, currChar))
                
                case ':':
                    tokens.append(Token(TokenType.COLON, currChar))

                case ',':
                    tokens.append(Token(TokenType.COMMA, currChar))

                case '"':
                    state = State.STRING

                case c if c == '-' or c.isdigit():
                    buffer = currChar
                    state = State.NUMBER

                case c if c in "tfn": # true, false, null
                    state = State.LITERAL
                    continue

                case _:
                    raise LexerError(f"Unexpected character '{currChar}'", index)

                
        elif state == State.STRING:
            # Reaching ESCAPE sequence
            if currChar == '\\':
                state = State.ESCAPE
            # Reaching end of string
            elif currChar == '"':
                tokens.append(Token(TokenType.STRING, buffer))
                # After the string is done, reset state machine to default
                state = state.DEFAULT
            else:
                buffer += currChar

        elif state == State.ESCAPE:
            if currChar in ESCAPE_MAP:
                buffer += ESCAPE_MAP[currChar]
                state = State.STRING
            elif currChar =='u':
                unicode_buffer = ''
                state = State.UNICODE_ESCAPE
            else:
                raise LexerError("Invalid escape character '{currChar}'", index)
    

        elif state == State.UNICODE_ESCAPE:
            if currChar in '0123456789ABCDEF':
                unicode_buffer += currChar
                if len(unicode_buffer) == 4:
                    try:
                        unicode_char = chr(int(unicode_buffer), 16)
                        buffer += unicode_char
                    except ValueError:
                        raise LexerError(f"Invalid Unicode escape sequence '\\u{unicode_buffer}'", index - 4)
                    state = State.STRING
            else:
                raise LexerError(f"Invalid Unicode escape sequence \\u{unicode_buffer}{currChar}'", index)

        elif state == State.NUMBER:

            if currChar in NUMBERS_VALID_CHARS:
                buffer += currChar
            else:

                try:
                    if '.' in buffer or 'e' in buffer.lower():
                        value = float(buffer)
                    else:
                        value = int(buffer)
                    tokens.append(Token(TokenType.NUMBER, value))

                except ValueError:
                    raise LexerError(f"Invalid number format '{buffer}'", index - len(buffer))

                state = State.DEFAULT
                buffer = ''
                continue

        elif state == State.LITERAL:

            if input_string[index:index+4] == 'true':
                tokens.append(Token(TokenType.TRUE, True))
                index += 3
            elif input_string[index:index+4] == 'null':
                tokens.append(Token(TokenType.NULL, None))
                index += 3
            elif input_string[index:index+5] == 'false':
                tokens.append(Token(TokenType.FALSE, False))
                index += 4
            else:
                raise LexerError("Invalid LITERAL", index - 1)
            
            state = state.DEFAULT

        index += 1

    if state == State.NUMBER:
        try:
            if '.' in buffer or 'e' in buffer.lower():
                value = float(buffer)
            else:
                value = int(buffer)
            tokens.append(Token(TokenType.NUMBER, value))
        except ValueError:
            raise LexerError(f"Invalid number format '{buffer}'", len(input_string) - len(buffer))
    elif state == State.STRING:
        raise LexerError("Unterminated string", len(input_string))
    elif state == State.LITERAL:
        raise LexerError(f"Incomplete literal '{buffer}'", len(input_string) - len(buffer))
    elif state == State.ESCAPE:
        raise LexerError("Incomplete escape sequence", len(input_string))
    elif state == State.UNICODE_ESCAPE:
        raise LexerError(f"Incomplete Unicode escape sequence '\\u{unicode_buffer}'", len(input_string))


    tokens.append(Token(TokenType.EOF, None))
    return tokens


def tokenize_from_file(file_path):
    """
    Tokenize JSON from a file.

    Args:
        file_path (str): Path to the JSON file

    Returns:
        list: List of tokens

    Raises:
        FileNotFoundError: If the file doesn't exist
        LexerError: If there's an error during tokenization
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return tokenize(content)
    except IOError as e:
        raise LexerError(f"Error reading file '{file_path}': {e}", 0)

def tokenize_from_string(json_string):
    """
    Tokenize JSON from a string.

    Args:
        json_string (str): JSON string to tokenize

    Returns:
        list: List of tokens

    Raises:
        LexerError: If there's an error during tokenization 
    """
    return tokenize(json_string)
