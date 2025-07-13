
class LexerError(Exception):
    def __init__(self, message, position):
        super().__init__(f"LexerError at position {position} : {message}"}
