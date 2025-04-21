from html_tokenize import HTMLToken, HTMLTokenType
from utilities import *
from enum import Enum


class TagInfo(Enum):
    TAG_NAME = 0
    ATTRIBUTE_NAME = 1
    ATTRIBUTE_VALUE = 2
    ATTRIBUTE_VALUE_JS = 3


class TagToken:
    def __init__(self, data_type: TagInfo, value: str):
        self.data_type: TagInfo = data_type
        self.value: str = value

    def __str__(self):
        return "<" f"{self.data_type}, {self.value}" ">"


_state = 0


def _generate_tokens(data: str) -> list[TagToken]:
    global _state

    # if _state != 0 and _state != 4:
    #     raise ValueError("Parsing error")

    generated_tokens: list[TagToken] = []

    lexeme = ""
    for i, c in enumerate(data):
        lexeme += c

        if _state == 0:
            if c == '<':
                _state = 1
            elif c.isalpha():
                _state = 4
            elif c == '"' or c == "'":
                _state = 6
            elif c == '{':
                _state = 6
            elif c not in [' ', '/', '>']:
                raise_error(data, c, i)

        elif _state == 1:
            if c.isalpha():
                _state = 2
                continue

            raise_error(data, c, i)

        elif _state == 2:
            if c == ' ' or c == '>':
                generated_tokens.append(TagToken(TagInfo.TAG_NAME, lexeme[1:-1]))
                lexeme = ""
                _state = 0
            elif not c.isalpha():
                raise_error(data, c, i)

        elif _state == 4:
            if c == '=':
                generated_tokens.append(TagToken(TagInfo.ATTRIBUTE_NAME, lexeme[:-1]))
                lexeme = ""
                _state = 0
            elif c != '-' and not c.isalpha():
                raise_error(data, c, i)

        elif _state == 6:
            if c == lexeme[0]:
                generated_tokens.append(TagToken(TagInfo.ATTRIBUTE_VALUE, lexeme[1:-1]))
                lexeme = ""
                _state = 0
            elif lexeme[0] == '{' and c == '}':
                generated_tokens.append(TagToken(TagInfo.ATTRIBUTE_VALUE_JS, lexeme[1:-1]))
                lexeme = ""
                _state = 0

    return generated_tokens


def tokenize_html_token(token: HTMLToken) -> list[TagToken]:
    if token.token_type != HTMLTokenType.TAG:
        return []

    tokens = _generate_tokens(token.lexeme)

    if _state == 6:
        raise ValueError(f"Unbalanced quote or curly brace in\n    {token.lexeme}")

    return tokens
