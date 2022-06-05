class Token:
    def __init__(self, data):
        self.data = data


class ColumnToken(Token):
    def __init__(self, name: str):
        super().__init__(name)


class ValueToken(Token):
    def __init__(self, value):
        super().__init__(value)


class NumberToken(ValueToken):
    def __init__(self, num: int):
        super().__init__(num)


class StringToken(ValueToken):
    def __init__(self, text: str):
        super().__init__(text)


class Tokenizer:
    def __init__(self, text: str):
        self._text = text
        self._idx = 0

    def advance(self):
        self._idx += 1

    def is_end(self):
        return self._idx == len(self._text)

    def get_char(self):
        if self._idx < len(self._text):
            return self._text[self._idx]
        raise RuntimeError

    def skip_whitespace(self):
        while not self.is_end() and (self.get_char().isspace() or self.get_char() in ['(', ')', ',']):
            self.advance()

    def read_token(self) -> Token:
        if self.get_char().isdigit() or self.get_char() == '-':
            num = ""
            while self.get_char().isdigit() or self.get_char() == '.' or self.get_char() == '-':
                num += self.get_char()
                self.advance()
            return NumberToken(int(num))
        elif self.get_char() == '\'':
            text = ""
            self.advance()
            while self.get_char() not in ['\'', ')', ','] and not self.get_char().isspace():
                text += self.get_char()
                self.advance()
            self.advance()
            return StringToken(text)
        elif self.get_char().isalpha():
            text = ""
            while self.get_char() not in ['(', ')', ','] and not self.get_char().isspace():
                text += self.get_char()
                self.advance()
            return ColumnToken(text)
        else:
            raise RuntimeError

    def __iter__(self):
        while not self.is_end():
            self.skip_whitespace()
            yield self.read_token()
            self.skip_whitespace()
