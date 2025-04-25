from parsing.html_to_js import transcribe_html
from typing import Optional
from pathlib import Path
import utilities
import threading
import logging
import time
import sys


_lock = threading.Lock()
_observers = []


def process_html(_file: Path, config: Optional[dict] = None):
    try:
        start_time = time.time()

        js_name = _file.name.replace(_file.suffix, ".js")
        with open(_file.with_name(js_name), "w") as f:
            js = transcribe_html(_file, config)
            js.minify = utilities.MINIFY_CODE
            f.write(str(js))

        end_time = time.time()
        logging.info(f"{_file.name} processed in {end_time - start_time:.4f} seconds")
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
    _lock.release()

    def process(src_path: str):
        _lock.acquire()
        utilities.update_properties(block)
        f = Path(src_path).resolve()
        if f.suffix == ".html" and (any_file or f in block["FILE"]):
            if "REPL_ID" in block:
                f_index = block["FILE"].index(f)
                block["FILE"].append(block["FILE"].pop(f_index))
                block["REPL_ID"].append(block["REPL_ID"].pop(f_index))

            process_html(f, block)
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
    observer.join()


def process_config(_file: Path):
    threads = []

    try:
        config_data = utilities.parse_config(_file)
        for block in config_data:
            if "WATCH" in block and block["WATCH"]:
                t = threading.Thread(target=watch_files, args=(block, ))
                t.start()
                threads.append(t)
                continue

            utilities.update_properties(block)
            files = block["FILE"] if block["FILE"] != "*" else utilities.list_html_files(block["PATH"])

            for f in files:
                process_html(f, block)
                if "REPL_ID" in block:
                    block["REPL_ID"].append(block["REPL_ID"].pop(0))
    except ValueError as e:
        logging.info("Error produced in " + str(_file.resolve()))
        logging.fatal(e.__str__())
        # raise  # debug

    if threads:
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            pass
        finally:
            for obs in _observers:
                obs.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(module)s:%(levelname)s: %(message)s", datefmt="%d %b %H:%M:%S"
    )

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
        if read_config:
            process_config(file)
        else:
            process_html(file)
            exit(0)
    elif file.is_dir():
        if read_config:
            logging.fatal("Specified path is not a config file")
            exit(1)

        for path in utilities.list_html_files(file):
            process_html(path)
