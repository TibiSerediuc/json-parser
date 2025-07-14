from error_handling import ParserError
from lexer import TokenType, Token

class Parser:
    def __init__(self):
        self.tokens = tokens
        self.index = 0


    def peek(self):
        # Peek the current token
        return self.tokens[self.index]

    def consume(self, expected_type = None):
        token = self.tokens[self.index]
        if expected_type and token.type != expected_type:
            raise ParserError(f"Expected {expected_type}, got {token.type}")
        self.index += 1
        return token

    def parse_value(self):
        token = self.peek()

        if token.type == TokenType.LEFT_BRACE:
            return self.parse_object()
        elif token.type == TokenType.LEFT_BRACKET:
            return self.parse_array()
        elif token.type == TokenType.STRING:
            return self.consume().value
        elif token.type == TokenType.NUMBER:
            return self.parse_number()
        elif token.type == TokenType.TRUE:
            self.consume()
            return True
        elif token.type == TokenType.FALSE:
            self.consume()
            return False
        elif token.type == TokenType.NULL:
            self.consume()
            return None
        else:
            raise ParserError(f"Unexpected token : {token}")


