from error_handling import ParserError
from lexer import TokenType


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def advance(self):
        self.index += 1

    def peek(self):
        # Peek the current token
        if self.index >= len(self.tokens):
            raise ParserError("Unexpected end of input")
        return self.tokens[self.index]

    def consume(self, expected_type=None):

        if self.index >= len(self.tokens):
            raise ParserError("Unexpected end of input")

        token = self.tokens[self.index]
        if expected_type and token.type != expected_type:
            raise ParserError(f"Expected {expected_type}, got {token.type}")
        self.advance()
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

    def parse_object(self):

        obj = {}
        self.consume(TokenType.LEFT_BRACE)

        if self.peek().type == TokenType.RIGHT_BRACE:
            self.consume()
            return obj

        while True:
            keyToken = self.consume(TokenType.STRING)
            self.consume(TokenType.COLON)
            value = self.parse_value()
            obj[keyToken.value] = value

            if self.peek().type == TokenType.COMMA:
                self.advance()
            elif self.peek().type == TokenType.RIGHT_BRACE:
                self.consume()
                break
            else:
                raise ParserError("Expected comma or right brace in object")

        return obj

    def parse_array(self):

        self.consume(TokenType.LEFT_BRACKET)
        array = []

        if self.peek().type == TokenType.RIGHT_BRACKET:
            self.consume()
            return array

        while True:

            value = self.parse_value()
            array.append(value)

            if self.peek().type == TokenType.COMMA:
                self.consume()
            elif self.peek().type == TokenType.RIGHT_BRACKET:
                self.consume()
                break
            else:
                raise ParserError("Expected comma or right bracket in array")

        return array

    def parse_number(self):
        return self.consume(TokenType.NUMBER).value
