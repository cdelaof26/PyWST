from pathlib import Path
import html_tokenize
import logging
import sys


def translate_html(_file: Path):
    with open(_file, "r") as f:
        data = f.readlines()
        tokens = html_tokenize.tokenize_file(data)

        for t in tokens:
            print(str(t))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        logging.error("A config file or HTML file to parse is required")
        exit(1)

    file = Path(sys.argv[1])
    if not file.exists():
        logging.error(f"The file '{file}' doesn't exist")
        exit(1)

    translate_html(file)
