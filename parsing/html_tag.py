from parsing.html_tokenize import HTMLToken, HTMLTokenType
from utilities import *
from enum import Enum


class TagInfo(Enum):
    TAG_NAME = 0
    ATTRIBUTE_NAME = 1
    ATTRIBUTE = 2


class TagToken:
    def __init__(self, data_type: TagInfo, value: str):
        self.data_type: TagInfo = data_type
        self.value: str = value

    def __str__(self):
        return "<" f"{self.data_type}, {self.value}" ">"


_state = 0
_quote = None


def _generate_tokens(data: str) -> list[TagToken]:
    global _state, _quote

    generated_tokens: list[TagToken] = []

    lexeme = ""
    i = 0
    while i < len(data):
        c = data[i]
        i += 1

        if _state == 0:
            if c == '<':
                lexeme += c
                _state = 1
            elif c.isalpha():
                lexeme += c
                _state = 4
            elif c == '/':
                _state = 14
            elif c != ' ' and c != '>':
                raise_error(data, c, i)

        elif _state == 1:
            if c.isalpha():
                lexeme += c
                _state = 2
            else:
                raise_error(data, c, i)

        elif _state == 2:
            if c == ' ' or c == '>':
                generated_tokens.append(TagToken(TagInfo.TAG_NAME, lexeme[1:]))
                lexeme = ""
                _state = 0
            elif c == '-' or c.isalnum():
                lexeme += c
            elif c == '/':
                _state = 12
            else:
                raise_error(data, c, i)

        elif _state == 4:
            if c == '>':
                generated_tokens.append(TagToken(TagInfo.ATTRIBUTE_NAME, lexeme))
                lexeme = ""
                _state = 0
            elif c == '=':
                lexeme += c
                _state = 8
            elif c == ' ':
                _state = 9
            elif c == '-' or c == ':' or c.isalnum():
                lexeme += c
            elif c == '/':
                _state = 13
            else:
                raise_error(data, c, i)

        elif _state == 6:
            lexeme += c
            if c == _quote != '{' or _quote == '{' and c == '}':
                generated_tokens.append(TagToken(TagInfo.ATTRIBUTE, lexeme))
                lexeme = ""
                _state = 0

        elif _state == 8:
            if c in ['"', "'", '{']:
                lexeme += c
                _state = 6
                _quote = c
            elif c == '=':
                raise_error(data, c, i)
            elif c != ' ':
                lexeme += c
                _state = 10

        elif _state == 9:
            if c == '=':
                lexeme += c
                _state = 8
            elif c != ' ':
                generated_tokens.append(TagToken(TagInfo.ATTRIBUTE_NAME, lexeme))
                lexeme = ""
                _state = 0
                i -= 1

        elif _state == 10:
            if c == ' ' or c == '>':
                generated_tokens.append(TagToken(TagInfo.ATTRIBUTE, lexeme))
                lexeme = ""
                _state = 0
            elif c not in ['"', "'", '{', '}']:
                lexeme += c
            else:
                raise_error(data, c, i)

        elif _state == 12:
            if c == '>':
                generated_tokens.append(TagToken(TagInfo.TAG_NAME, lexeme[1:]))
                lexeme = ""
                _state = 0
                continue

            raise_error(data, c, i)

        elif _state == 13:
            if c == '>':
                generated_tokens.append(TagToken(TagInfo.ATTRIBUTE_NAME, lexeme))
                lexeme = ""
                _state = 0
                continue

            raise_error(data, c, i)

        elif _state == 14:
            if c == '>':
                _state = 15
                continue

            raise_error(data, c, i)

        elif _state == 15:
            raise_error(data, c, i)

    return generated_tokens


def reset_html_tag_tokenize():
    global _state, _quote
    _state = 0
    _quote = None


def tokenize_html_token(token: HTMLToken) -> list[TagToken]:
    global _state

    if token.token_type != HTMLTokenType.TAG:
        return []

    tokens = _generate_tokens(token.lexeme)

    if _state == 6:
        raise ValueError(f"Unbalanced quote or curly brace in\n    {token.lexeme}")

    if _state == 15:
        _state = 0

    return tokens
