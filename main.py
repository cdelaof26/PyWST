from parsing.html_to_js import transcribe_html
from typing import Optional
from pathlib import Path
import utilities
import threading
import argparse
import logging
import time


_lock = threading.Lock()
_observers = []


def process_html(_file: Path, config: Optional[dict] = None):
    try:
        start_time = time.time()

        js_name = _file.name.replace(_file.suffix, ".js") if _file.suffix else f"{_file.name}.js"
        js = transcribe_html(_file, config)
        js.minify = utilities.MINIFY_CODE
        with open(_file.with_name(js_name), "w") as f:
            f.write(str(js))

        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time > 1:
            logging.info(f"{_file.name} processed in {elapsed_time: .2f} seconds")
        else:
            logging.info(f"{_file.name} processed in {elapsed_time * 1000: .0f} ms")
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
    except AssertionError:
        logging.info("Error produced in " + str(_file.resolve()))
        logging.fatal("Specified file doesn't contain valid HTML data")
        # raise  # debug


def watch_files(block: dict):
    global _lock

    from watchdog.events import DirModifiedEvent, FileModifiedEvent
    from watchdog.events import DirCreatedEvent, FileCreatedEvent
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    files = block["FILE"]
    any_file = files and files[0] == "*"

    _lock.acquire()
    utilities.update_properties(block)
    for f in files if not any_file else utilities.list_html_files(block["PATH"]):
        process_html(f, block)
        if "REPL_ID" in block:
            block["REPL_ID"].append(block["REPL_ID"].pop(0))
        if "PARAMS" in block:
            block["PARAMS"].append(block["PARAMS"].pop(0))
    _lock.release()

    def process(src_path: str):
        _lock.acquire()
        utilities.update_properties(block)
        _f = Path(src_path).resolve()
        if _f.suffix == ".html" and (any_file or _f in block["FILE"]):
            if not any_file:
                f_index = block["FILE"].index(_f)
                block["FILE"].insert(0, block["FILE"].pop(f_index))
                if "REPL_ID" in block:
                    block["REPL_ID"].insert(0, block["REPL_ID"].pop(f_index))
                if "PARAMS" in block:
                    block["PARAMS"].insert(0, block["PARAMS"].pop(f_index))

            process_html(_f, block)
        _lock.release()

    class TranscriptEventHandler(FileSystemEventHandler):
        def on_modified(self, event: DirModifiedEvent | FileModifiedEvent):
            if event.is_directory:
                return
            process(event.src_path)

        def on_created(self, event: DirCreatedEvent | FileCreatedEvent):
            if event.is_directory:
                return
            process(event.src_path)

    event_handler = TranscriptEventHandler()
    observer = Observer()
    observer.schedule(event_handler, block["PATH"], recursive=True)
    _observers.append(observer)
    observer.start()


def process_config_block(block: dict):
    if "WATCH" in block and block["WATCH"]:
        watch_files(block)
        return

    utilities.update_properties(block)
    files = block["FILE"] if block["FILE"] != "*" else utilities.list_html_files(block["PATH"])

    for _f in files:
        process_html(_f, block)
        if "REPL_ID" in block:
            block["REPL_ID"].append(block["REPL_ID"].pop(0))
        if "PARAMS" in block:
            block["PARAMS"].append(block["PARAMS"].pop(0))


def wait_observers():
    global _observers
    if _observers:
        try:
            for obs in _observers:
                obs.join()
        except KeyboardInterrupt:
            pass
        finally:
            for obs in _observers:
                obs.stop()


def process_config(_file: Path):
    try:
        config_data = utilities.parse_config(_file)
    except ValueError as e:
        logging.info("Error produced in " + str(_file.resolve()))
        logging.fatal(e.__str__())
        # raise  # debug
        return

    for block in config_data:
        process_config_block(block)

    wait_observers()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(module)s:%(levelname)s: %(message)s", datefmt="%d %b %H:%M:%S"
    )

    args_parser = argparse.ArgumentParser(prog="main.py", description="Python HTML to JS transcriptor")
    bool_choices = ["yes", "no"]

    args_parser.add_argument("-c", "--config", action="store_true", help="Specifies that a file is a config file")
    args_parser.add_argument("-f", "--file", action="append", required=True,
                             help="Specify a config, directory or HTML file path")
    args_parser.add_argument("-b", "--behavior", default="ret",
                             help="What the script does, return or replace HTMLElements")
    args_parser.add_argument("-id", "--idrepl", action="append", help="Replacement ID")
    args_parser.add_argument("-uid", "--uidrepl", help="Replacement ID for all components")
    args_parser.add_argument("-p", "--params", help="Parameters used inside the HTML")
    args_parser.add_argument("-o", "--onload", choices=bool_choices, help="Whether the script should run onload")
    args_parser.add_argument("-w", "--watch", choices=bool_choices,
                             help="Whether PyWST should watch for filesystem changes")
    args_parser.add_argument("-m", "--minify", choices=bool_choices,
                             help="Whether PyWST should minify generated scripts")
    args_parser.add_argument("--ictag", choices=bool_choices,
                             help="Whether PyWST should ignore invalid characters inside closing tags")
    args_parser.add_argument("--mctag", choices=bool_choices,
                             help="Whether PyWST should ignore mismatching closing tags")
    args_parser.add_argument("--entdec", choices=bool_choices,
                             help="Whether PyWST should add a function to decode HTML entities")

    arguments = args_parser.parse_args()

    read_config = arguments.config
    amount_of_files = len(arguments.file)
    if amount_of_files != 1 and read_config:
        logging.fatal("Only one config file can be processed at a time")
        exit(1)

    if read_config:
        file = Path(arguments.file[0])
        if not file.exists():
            logging.fatal(f"File '{file}' doesn't exist")
            exit(1)

        if file.is_dir():
            logging.fatal("Specified path is not a config file")
            exit(1)

        process_config(file)
        exit(0)

    try:
        config_args = utilities.args_to_config(arguments)
        # print(config_args)
    except ValueError as ex:
        logging.fatal(ex.__str__())
        # raise  # debug
        exit(1)

    process_config_block(config_args)
    wait_observers()
