from enum import Enum
from error_handling import LexerError

# All possible tokens in a JSON string
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
    
# States used inside the state machine for robust handling
class State(Enum):
    DEFAULT = 0
    STRING = 1
    NUMBER = 2
    LITERAL = 3
    ESCAPE = 4

# Used to trivially check whether the token is a single character token
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

class Token:

    def __init__(self, type_: TokenType, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token: {self.type}, {repr(self.value)})"


def tokenize(input_string):
    state = State.DEFAULT
    index = 0
    tokens = []
    buffer = ''
    
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
            else:
                raise LexerError("Invalid escape character '{currChar}'", index)
            state = state.STRING


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
                buffer = input_string[index:index+4]
                tokens.append(Token(TokenType.TRUE, buffer))
            elif input_string[index:index+4] == 'null':
                tokens.append(Token(TokenType.NULL, None))
            elif input_string[index:index+5] == 'false':
                buffer = input_string[index:index+5]
                tokens.append(Token(TokenType.FALSE, buffer))      
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

    tokens.append(Token(TokenType.EOF, None))
    return tokens


if __name__ == "__main__":

    input_string = r'{"name": "John", "age": 30, "is_student": false, "grades": [90, 85, 88], "address": null}'
    input_ = r'{"key": "v\nalu\\e", "number": 123}'


    try:
        tokens = tokenize(input_string)
        print("Tokens for input string: ")
        for token in tokens:
            print(token)
    except LexerError:
        print(f"Lexer Error: {e}")
