from utilities import *
from enum import Enum
import re


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
_lexeme = ""
_quote = None


def generate_tokens(data: str, line: int = -1) -> list[HTMLToken]:
    global _state, _lexeme, _quote

    if _state not in [0, 4, 11, 15]:
        raise ValueError(f"Parsing error |{_state=}|")

    generated_tokens: list[HTMLToken] = []

    i = 0
    is_been_in_13 = False
    while i < len(data):
        c = data[i]
        i += 1

        if _state == 0:
            _lexeme += c
            if c == '<':
                _state = 1
                continue

            _state = 13

        elif _state == 1:
            _lexeme += c
            if c == '!':
                _state = 2
            elif c == '/':
                _state = 8
            elif c.isalpha():
                if is_been_in_13:  # State 14 from 11
                    is_been_in_13 = False
                    i -= 2
                    generated_tokens.append(HTMLToken(HTMLTokenType.DATA, line, i, _lexeme[:-2]))
                    _lexeme = ""
                    _state = 0
                    continue

                _state = 11
            else:
                _state = 13

        elif _state == 2 or _state == 3:
            _lexeme += c
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
                _lexeme = ""
            elif c != '-':
                _state = 4

        elif _state == 8:
            _lexeme += c
            if c.isalpha():
                if is_been_in_13:  # State 14 from 9
                    is_been_in_13 = False
                    i -= 3
                    generated_tokens.append(HTMLToken(HTMLTokenType.DATA, line, i, _lexeme[:-3]))
                    _lexeme = ""
                    _state = 0
                    continue

                _state = 9
                continue

            raise_error(data, c, i, line)

        elif _state == 9:
            _lexeme += c
            if c == '>':
                generated_tokens.append(HTMLToken(HTMLTokenType.CLOSING_TAG, line, i, _lexeme))
                _lexeme = ""
                _state = 0

            elif not c.isalnum() and c != '-':
                raise_error(data, c, i, line)

        elif _state == 11:
            _lexeme += c
            if c in ['"', "'", '{']:
                _state = 15
                _quote = c
            elif c == '>':
                generated_tokens.append(HTMLToken(HTMLTokenType.TAG, line, i, _lexeme))
                _lexeme = ""
                _state = 0
            elif c == '<':
                raise_error(data, c, i, line)

        elif _state == 13:
            is_been_in_13 = True
            _lexeme += c
            if c == '<':
                _state = 1

        elif _state == 15:
            _lexeme += c
            if c == _quote or _quote == '{' and c == '}':
                _quote = None
                _state = 11

    if _state == 13:
        generated_tokens.append(HTMLToken(HTMLTokenType.DATA, line, i, _lexeme))
        _lexeme = ""
        _state = 0

    return generated_tokens


def tokenize_file(file_data: list[str]) -> list[HTMLToken]:
    tokens = []

    is_script = False
    processed_script = []
    index_difference = 0

    for i, line in enumerate(file_data):
        if line.startswith(" "):
            raise ValueError("Please run fix_indent.py or change the indentation to tabs and then try again")

        line = re.sub(r"^\t+", "", line)

        if not line.strip():
            continue

        # TODO: Find if there's another workaround

        # QuickFix1: if a previous tag was script then anything becomes DATA until the close
        #            is found
        # QuickFix2: if the line contains an opening and closing script tag then the
        #            tag will be processed separately and replaced with <rps>.
        #            After parsing <rps> the processed tag will be placed back

        # tokens += generate_tokens(line, i + 1)

        # TODO: Implement QuickFixes for style tag

        if "<script" in line and "</script" in line:  # Handle one line script
            scripts = re.findall("<script.*?>.*?</script.*?>", line)
            for s in scripts:
                data = re.sub(r"^<script.*?>", "", re.sub(r"</script.*?>$", "", s))
                if not data:
                    continue

                script_tag, script_tag_close = s.split(data)

                script_tag_start = line.index(script_tag)
                data_start = script_tag_start + len(script_tag)
                script_tag_close_start = data_start + len(data)

                line = line.replace(s, "<rps>")

                # This position is required by the following tokens
                # otherwise following tokens will show an incorrect column position
                processed_script.append(len(s) - len("<rps>"))

                processed_script.append([
                    HTMLToken(HTMLTokenType.TAG, i, script_tag_start, script_tag),
                    HTMLToken(HTMLTokenType.DATA, i, data_start, data),
                    HTMLToken(HTMLTokenType.CLOSING_TAG, i, script_tag_close_start, script_tag_close)
                ])

        if is_script and not line.startswith("</script"):
            tokens.append(HTMLToken(HTMLTokenType.DATA, i, 0, line))
            continue

        _tokens = generate_tokens(line, i + 1)
        for t in _tokens:
            if t.token_type == HTMLTokenType.TAG and t.lexeme == "<rps>":
                index_difference += processed_script.pop(0)
                for rps in processed_script[0]:
                    tokens.append(rps)
                processed_script.pop(0)
                continue

            if t.token_type == HTMLTokenType.TAG and t.lexeme.startswith("<script"):
                is_script = True
            if t.token_type == HTMLTokenType.CLOSING_TAG and t.lexeme.startswith("</script"):
                is_script = False

            t.column += index_difference
            tokens.append(t)

    if _state == 4:
        raise ValueError("Source contains unclosed comments")

    if _state == 15:
        raise ValueError("Source contains unbalanced quotes or curly braces")

    return tokens
