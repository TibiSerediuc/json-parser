# For start, I want to write a simple lexer that work on JSON strings

from enum import Enum

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
    
class State(Enum):
    DEFAULT = 0
    STRING = 1
    NUMBER = 2
    LITERAL = 3
    ESCAPE = 4

# Used to trivially check whether a token to be formed for a single character token
SINGLE_CHAR_TOKENS = {
        TokenType.LEFT_BRACE.value,
        TokenType.RIGHT_BRACE.value,
        TokenType.LEFT_BRACKET.value,
        TokenType.RIGHT_BRACKET.value,
        TokenType.COLON.value,
        TokenType.COMMA.value
}

ESCAPE_SEQUENCE_CHARS = {
        '"',
        '\\',
        '/',
        'b',
        'f',
        'n',
        'r',
        't'
}

class Token:

    def __init__(self, type_: TokenType, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token: {self.type}, {repr(self.value)})"


if __name__ == "__main__":

    input_string = '{"key": "value", "number": 123}'
    state = State.DEFAULT
    index = 0
    LexerOutput = []

    prevChar = ''
    buffer = ''
    
    while index < len(input_string):

        currChar = input_string[index]
        currToken = Token(None, None)

        if state == State.DEFAULT:
            buffer = ''
    
            match currChar:
                case '{':                
                    currToken.type = TokenType.LEFT_BRACE

                case '}':
                    currToken.type = TokenType.RIGHT_BRACE

                case '[':
                    currToken.type = TokenType.LEFT_BRACKET

                case ']':
                    currToken.type = TokenType.RIGHT_BRACKET
                
                case ':':
                    currToken.type = TokenType.COLON

                case ',':
                    currToken.type = TokenType.COMMA

                case '"':
                    state = State.STRING

                case c if c == '-' or '0' <= c <= '9':
                    state = State.NUMBER

                case c if c == 't' or c == 'f' or c == 'n':
                    prevChar = currChar
                    state = State.LITERAL

        elif state == State.STRING:
            # Reaching ESCAPE sequence
            if currChar == '\\':
                state = State.ESCAPE
            # Reaching end of string
            elif currChar == '"':
                currToken.type = TokenType.NUMBER
            else:
                buffer += currChar

        elif state == State.ESCAPE:

            currToken = Token(None, None)
            if currChar in ESCAPE_SEQUENCE_CHARS:
                pass
                

            pass
        elif state == State.NUMBER:
            pass
        elif state == State.LITERAL:
            pass

        if currChar in SINGLE_CHAR_TOKENS:
            LexerOutput.append(currToken)
        index += 1

    
    for token in LexerOutput:
        print(token)
