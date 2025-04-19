from enum import Enum


class _TokenType(Enum):
    TAG = 0
    CLOSING_TAG = 1
    DATA = 2


class HTMLToken:
    def __init__(self, token_type: _TokenType, line: int, column: int, lexeme: str = ""):
        self.token_type: _TokenType = token_type
        self.lexeme: str = lexeme
        self.line: int = line
        self.column: int = column

    def __str__(self):
        return "{" f"{self.token_type.name}, {_escape_whitespace(self.lexeme)}, {self.line}" "}"


def _escape_whitespace(data: str) -> str:
    for sequence, repl in zip(["\t", "\n", "\r", "\b", "\f"], ["\\t", "\\n", "\\r", "\\b", "\\f"]):
        data = data.replace(sequence, repl)
    return data


def _remove_whitespace(data: str) -> str:
    for sequence in ["\t", "\n", "\r", "\b", "\f"]:
        data = data.replace(sequence, " ")
    return data


def _raise_error(data: str, c: str, i: int, line: int):
    data = _remove_whitespace(data)
    c = _escape_whitespace(c)

    ex = f"Illegal character '{c}', char.no {i}"
    if line != -1:
        ex += f", line {line}\n"
        spacing = " " * len(str(line))
        ex += f"  {line}  {data}" + f"\n  {spacing}  " + "-" * (i - 1) + "^"
    raise ValueError(ex)


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
                    generated_tokens.append(HTMLToken(_TokenType.DATA, line, i, lexeme[:-2]))
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
                    generated_tokens.append(HTMLToken(_TokenType.DATA, line, i, lexeme[:-3]))
                    lexeme = ""
                    _state = 0
                    continue

                _state = 9
                continue

            _raise_error(data, c, i, line)

        elif _state == 9:
            lexeme += c
            if c == '>':
                generated_tokens.append(HTMLToken(_TokenType.CLOSING_TAG, line, i, lexeme))
                lexeme = ""
                _state = 0

            elif not c.isalpha():
                _raise_error(data, c, i, line)

        elif _state == 11:
            lexeme += c
            if c == '>':
                generated_tokens.append(HTMLToken(_TokenType.TAG, line, i, lexeme))
                lexeme = ""
                _state = 0

        elif _state == 13:
            is_been_in_13 = True
            lexeme += c
            if c == '<':
                _state = 1

    if _state == 13:
        generated_tokens.append(HTMLToken(_TokenType.DATA, line, i, lexeme))
        _state = 0

    return generated_tokens


def tokenize_file(file_data: list[str]) -> list[HTMLToken]:
    tokens = []

    for i, l in enumerate(file_data):
        tokens += generate_tokens(l, i + 1)

    if _state == 4:
        raise ValueError("Unclosed comment")

    return tokens
