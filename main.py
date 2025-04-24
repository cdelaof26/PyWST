from parsing.html_to_js import transcribe_html
from typing import Optional
from pathlib import Path
import utilities
import logging
import time
import sys


def process_html(_file: Path, config: Optional[dict] = None):
    try:
        start_time = time.time()

        js_name = _file.name.replace(_file.suffix, ".js")
        with open(_file.with_name(js_name), "w") as f:
            js = transcribe_html(_file, config)
            js.minify = utilities.MINIFY_CODE
            f.write(str(js))

        end_time = time.time()
        date = time.strftime("%d %b %H:%M:%S", time.localtime(end_time))
        logging.info(f"{date} {_file.name} processed in {end_time - start_time:.2f} seconds")
    except ValueError as e:
        logging.info("Error produced in " + str(_file.resolve()))
        logging.fatal(e.__str__())
        # raise  # debug
    except ReferenceError as e:
        logging.info("Error produced in " + str(_file.resolve()))
        if utilities.IGNORE_MISMATCHING_CLOSING_TAGS:
            logging.warning("This error might be caused by IGNORE_MISMATCHING_CLOSING_TAGS")
        logging.fatal(e.__str__())
        # raise  # debug


def process_config(_file: Path):
    properties = {
        "ALLOW_ANYTHING_IN_CLOSE_TAGS": False,
        "IGNORE_MISMATCHING_CLOSING_TAGS": False,
        "AUTOMATICALLY_DECODE_HTML_ENTITIES": True,
        "MINIFY_CODE": True
    }

    def update_properties(data_block: dict):
        for i, name_default in enumerate(properties.items()):
            name, default = name_default
            utilities.set_property(i, data_block[name] if name in data_block else default)

    try:
        config_data = utilities.parse_config(_file)
        for block in config_data:
            if "WATCH" in block and block["WATCH"]:
                logging.info("Watch is unavailable")
                continue

            update_properties(block)

            files = block["FILE"] if block["FILE"] != "*" else utilities.list_html_files(block["PATH"])

            for f in files:
                process_html(f, block)
                if "REPL_ID" in block:
                    block["REPL_ID"].append(block["REPL_ID"].pop(0))
    except ValueError as e:
        logging.info("Error produced in " + str(_file.resolve()))
        logging.fatal(e.__str__())
        # raise  # debug


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    args_no = len(sys.argv) - 1

    if args_no < 1:
        logging.fatal("A config file, an HTML file or directory to parse is required")
        exit(1)

    read_config = False
    if args_no == 2:
        if sys.argv[1] != "-c":
            logging.fatal(f"Invalid option '{sys.argv[1]}'")
            exit(1)

        read_config = True
        sys.argv[1], sys.argv[2] = sys.argv[2], sys.argv[1]

    file = Path(sys.argv[1])
    if not file.exists():
        logging.fatal(f"The specified route '{file}' doesn't exist")
        exit(1)

    if file.is_file():
        (process_config if read_config else process_html)(file)
        exit(0)

    if read_config:
        logging.fatal("Specified path is not a config file")
        exit(1)

    for path in utilities.list_html_files(file):
        process_html(path)
