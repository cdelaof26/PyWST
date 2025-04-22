from html_to_js import transcribe_html
from utilities import MINIFY_CODE
from pathlib import Path
import logging
import sys


def process_html(_file: Path):
    try:
        js_name = _file.name.replace(_file.suffix, ".js")
        with open(_file.with_name(js_name), "w") as f:
            js = transcribe_html(_file)
            js.minify = MINIFY_CODE
            f.write(str(js))
    except ValueError as e:
        logging.info("Error produced in " + str(_file.resolve()))
        logging.fatal(e.__str__())
        # raise  # debug


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        logging.fatal("A config file, an HTML file or directory to parse is required")
        exit(1)

    file = Path(sys.argv[1])
    if not file.exists():
        logging.fatal(f"The specified route '{file}' doesn't exist")
        exit(1)

    if file.is_file():
        process_html(file)
        exit(0)

    directories = [file]
    files = []
    while directories:
        directory = directories.pop(0)
        for element in directory.iterdir():
            if element.is_file() and element.suffix == ".html":
                files.append(element)
            elif element.is_dir():
                directories.append(element)

    for f in files:
        process_html(f)
