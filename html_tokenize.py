from utilities import *
from enum import Enum


class HTMLTokenType(Enum):
    TAG = 0
    CLOSING_TAG = 1
    DATA = 2


class HTMLToken:
    def __init__(self, token_type: HTMLTokenType, line: int, column: int, lexeme: str = ""):
        self.token_type: HTMLTokenType = token_type
        self.lexeme: str = lexeme
        self.line: int = line
        self.column: int = column

    def __str__(self):
        return "{" f"{self.token_type.name}, {escape_whitespace(self.lexeme)}, {self.line}" "}"


_state = 0


def generate_tokens(data: str, line: int = -1) -> list[HTMLToken]:
    global _state

    if _state != 0 and _state != 4:
        raise ValueError("Parsing error")

    generated_tokens: list[HTMLToken] = []

    lexeme = ""
    i = 0
    is_been_in_13 = False
    while i < len(data):
        c = data[i]
        i += 1

        if _state == 0:
            lexeme += c
            if c == '<':
                _state = 1
                continue

            _state = 13

        elif _state == 1:
            lexeme += c
            if c == '!':
                _state = 2
            elif c == '/':
                _state = 8
            elif c.isalpha():
                if is_been_in_13:  # State 14 from 11
                    is_been_in_13 = False
                    i -= 2
                    generated_tokens.append(HTMLToken(HTMLTokenType.DATA, line, i, lexeme[:-2]))
                    lexeme = ""
                    _state = 0
                    continue

                _state = 11
            else:
                _state = 13

        elif _state == 2 or _state == 3:
            lexeme += c
            if c == '-':
                _state += 1
                continue

            _state = 13

        elif _state == 4:
            if c == '-':
                _state = 5

        elif _state == 5:
            if c == '-':
                _state = 6
                continue

            _state = 4

        elif _state == 6:
            if c == '>':
                _state = 0
                lexeme = ""
            elif c != '-':
                _state = 4

        elif _state == 8:
            lexeme += c
            if c.isalpha():
                if is_been_in_13:  # State 14 from 9
                    is_been_in_13 = False
                    i -= 3
                    generated_tokens.append(HTMLToken(HTMLTokenType.DATA, line, i, lexeme[:-3]))
                    lexeme = ""
                    _state = 0
                    continue

                _state = 9
                continue

            raise_error(data, c, i, line)

        elif _state == 9:
            lexeme += c
            if c == '>':
                generated_tokens.append(HTMLToken(HTMLTokenType.CLOSING_TAG, line, i, lexeme))
                lexeme = ""
                _state = 0

            elif not c.isalpha():
                raise_error(data, c, i, line)

        elif _state == 11:
            lexeme += c
            if c == '>':
                generated_tokens.append(HTMLToken(HTMLTokenType.TAG, line, i, lexeme))
                lexeme = ""
                _state = 0

        elif _state == 13:
            is_been_in_13 = True
            lexeme += c
            if c == '<':
                _state = 1

    if _state == 13:
        generated_tokens.append(HTMLToken(HTMLTokenType.DATA, line, i, lexeme))
        _state = 0

    return generated_tokens


def tokenize_file(file_data: list[str]) -> list[HTMLToken]:
    tokens = []

    for i, l in enumerate(file_data):
        if l.startswith(" "):
            raise ValueError("Please run fix_indent.py or change the indentation to tabs and then try again")

        tokens += generate_tokens(l, i + 1)

    if _state == 4:
        raise ValueError("Found unclosed comment")

    return tokens
