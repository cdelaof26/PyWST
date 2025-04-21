from html_tokenize import HTMLTokenType, HTMLToken, tokenize_file
from html_tag import tokenize_html_token
from pathlib import Path
import logging
import sys
import re


def translate_html(_file: Path):
    with open(_file, "r") as f:
        data = f.readlines()
        tokens = tokenize_file(data)

        # Join all continuous DATA tokens and delete empty ones
        i = 0
        start = -1
        data_token = None
        while i < len(tokens):
            t: HTMLToken = tokens[i]
            if t.token_type != HTMLTokenType.DATA:
                if start == -1:
                    i += 1
                    continue

                data_token.lexeme = re.sub("^\n+", "", re.sub("\n+$", "", data_token.lexeme))
                if data_token.lexeme:
                    tokens = tokens[:start + 1] + tokens[i:]
                    tokens[start] = data_token
                    i = start + 1
                else:
                    tokens = tokens[:start] + tokens[i:]
                    i = start

                start = -1
                continue

            if start == -1:
                data_token = t
                start = i
                i += 1
                continue

            data_token.lexeme += re.sub("^\t+", "", t.lexeme)
            i += 1

        tokens: list

        i = 0
        while i < len(tokens):
            token_data = tokenize_html_token(tokens[i])
            if token_data:
                tokens[i] = token_data

            if isinstance(tokens[i], list):
                for t in tokens[i]:
                    print("   ", str(t))
            else:
                print(str(tokens[i]))

            i += 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        logging.error("A config file or HTML file to parse is required")
        exit(1)

    file = Path(sys.argv[1])
    if not file.exists():
        logging.error(f"The file '{file}' doesn't exist")
        exit(1)

    try:
        translate_html(file)
    except ValueError as e:
        logging.fatal(e.__str__())
        # raise  # debug
