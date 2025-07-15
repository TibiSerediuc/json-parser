class LexerError(Exception):
    def __init__(self, message, position):
        super().__init__(f"LexerError at position {position} : {message}")


class ParserError(Exception):
    def __init__(self, message):
        super().__init__(f"ParserError at position : {message}")
