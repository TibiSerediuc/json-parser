# For start, I want to write a simple lexer that work on JSON strings

from enum import Enum
from error_handling import LexerError

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


if __name__ == "__main__":

    input_string = r'{"name": "John", "age": 30, "is_student": false, "grades": [90, 85, 88], "address": null}'
    input_ = r'{"key": "v\nalu\\e", "number": 123}'
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
                    buffer += currChar
                    state = State.NUMBER

                case c if c == 't' or c == 'f' or c == 'n':
                    state = State.LITERAL

        elif state == State.STRING:
            # Reaching ESCAPE sequence
            if currChar == '\\':
                state = State.ESCAPE
            # Reaching end of string
            elif currChar == '"':
                currToken.type = TokenType.STRING
                currToken.value = buffer
                LexerOutput.append(currToken)

                # After the string is done, reset state machine to default
                state = state.DEFAULT
            else:
                buffer += currChar

        elif state == State.ESCAPE:
            if currChar in ESCAPE_MAP:
                buffer += ESCAPE_MAP[currChar]
            else:
                raise LexerError("Invalid escape character", index)
            state = state.STRING




        elif state == State.NUMBER:

            nextIndex = index
            firstDecimalPoint = False
            firstExponentSymbol = False

            while nextIndex < len(input_string) and input_string[nextIndex] in NUMBERS_VALID_CHARS:

                nextChar = input_string[nextIndex]

                if nextChar == '.':
                    if firstDecimalPoint == False:
                        buffer += nextChar
                        firstDecimalPoint = True
                    else:
                        raise LexerError("Number with multiple decimal points", index)

                if nextChar == 'e' or nextChar == 'E':
                    if firstExponentSymbol == False:
                        buffer += nextChar
                        firstExponentSymbol = True
                    else:
                        raise LexerError("Number with multiple exponent symbols", index)

                buffer += nextChar
                nextIndex += 1

            currToken.type = TokenType.NUMBER
            currToken.value = buffer
            LexerOutput.append(currToken)
            state = state.DEFAULT



        elif state == State.LITERAL:

            if input_string[index-1:index+3] == 'true':
                buffer += input_string[index-1:index+3]
                currToken.type = TokenType.TRUE
            elif input_string[index-1:index+3] == 'null':
                currToken.type = TokenType.NULL
            elif input_string[index-1:index+4] == 'false':
                currToken.type = TokenType.FALSE               
            else:
                raise LexerError("Invalid LITERAL", index - 1)
            
            LexerOutput.append(currToken)
            state = state.DEFAULT

        if currChar in SINGLE_CHAR_TOKENS:
            LexerOutput.append(currToken)
        index += 1

    print('\n') 
    for token in LexerOutput:
        print(token)
