from pathlib import Path
import questionary
import logging
import re


def valid_path(directory: str) -> bool:
    p = Path(directory)
    return p.exists() and p.is_dir()


def valid_un_id(element_id: str) -> bool:
    return element_id and re.sub(r"[a-zA-Z][\w.:_-]+", "", element_id) == ""


def valid_id(element_id: str) -> bool:
    if not element_id:
        return True

    return re.sub(r"[a-zA-Z][\w.:_-]+", "", element_id) == ""


def valid_js_params(_params: str) -> bool:
    _params = _params.strip()
    if not _params:
        return True

    split = _params.split(",")
    for p in split:
        p = p.strip()
        if not p or re.sub(r"[a-zA-Z_]\w+", "", p):
            return False

    return True


def config_not_taken(name: str):
    return name and name not in config_names


def retrieve_files(path: str) -> tuple[bool, list[str]]:
    try:
        parent = Path(path).resolve()
        directories = [parent]
        _files = []
        while directories:
            directory = directories.pop(0)
            for element in directory.iterdir():
                if element.is_file() and element.suffix.lower() == ".html":
                    name = str(element.resolve()).replace(str(parent), "")
                    _files.append(name[1:] if name.startswith("/") else name)
                elif element.is_dir():
                    directories.append(element)

        return len(_files) > 0, _files
    except PermissionError as e:
        logging.error(e)
        return False, []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config_names = []

    file_data = questionary.form(
        file_name=questionary.text(
            "Enter a name for the config file", default="config", validate=lambda x: len(x) > 0
        ),
        saving_path=questionary.path(
            "Where should it be saved?", default=str(Path.cwd()), validate=valid_path
        )
    ).ask()

    if file_data is None:
        exit(1)

    config_file_path = Path(file_data["saving_path"]).joinpath(file_data["file_name"]).resolve()

    overwrite = questionary.confirm(
        f"Overwrite '{file_data['file_name']}'?", default=False
    ).skip_if(not config_file_path.exists(), default=True).ask()

    if not overwrite:
        exit(1)

    config_file = open(config_file_path, "w")
    config_file.write("#     PyWST config file\n")
    config_file.write("# Generated with config.py\n")
    config_file.write("# More information at https://github.com/cdelaof26/PyWST/blob/main/config/sample\n\n")

    create_config = True
    configurations_written = 0
    last_default = 1
    default_name = "newConfig"

    while create_config:
        try:
            while not config_not_taken(default_name):
                default_name = f"newConfig{last_default}"
                last_default += 1

            new_config = questionary.text(
                "Enter a name for the config", default=default_name, validate=config_not_taken
            ).unsafe_ask()

            behavior_prop = questionary.select(
                "What should functions do?",
                choices=["Replace elements given an elementId", "Return the component"]
            ).unsafe_ask()

            behavior_prop = "replace" if "Replace" in behavior_prop else "return"

            use_un_repl_id = questionary.confirm(
                "All components replace the same elementId?", default=False
            ).skip_if(behavior_prop == "return", default=False).unsafe_ask()

            un_repl_id = questionary.text(
                "Enter the elementId", validate=valid_un_id
            ).skip_if(not use_un_repl_id).unsafe_ask()

            _use_params = questionary.select(
                "Do you want to specify parameters for every component?",
                choices=["Yes",
                         "No, I want to specify only one set of parameters for all components",
                         "No, my components do not require parameters"]
            ).unsafe_ask()

            use_single_params_set = "one set" in _use_params
            use_params = "Yes" in _use_params or use_single_params_set

            single_params = questionary.text(
                "Enter the parameters separated by comma", validate=valid_js_params
            ).skip_if(not use_single_params_set).unsafe_ask()

            files_not_found = True
            while files_not_found:
                files_path = questionary.path(
                    "Where are the HTML files stored?", default=file_data["saving_path"], validate=valid_path
                ).unsafe_ask()

                success, found_files = retrieve_files(files_path)
                if success:
                    files_not_found = False
                    break

                logging.info("No HTML files were found...")
                if not questionary.confirm("Do you want to try again?").unsafe_ask():
                    break

            if files_not_found:
                break

            specify_each_file = questionary.confirm(
                "Would you like to specify each file?", default=False
            ).skip_if(
                behavior_prop == "replace" and not use_un_repl_id or (use_params and not use_single_params_set),
                default=True
            ).unsafe_ask()

            files = questionary.checkbox(
                "Select all the files to include", choices=found_files
            ).skip_if(not specify_each_file, default=["*"]).unsafe_ask()

            repl_id = []
            params = []
            if not use_un_repl_id and behavior_prop == "replace":
                for f in files:
                    repl_id.append(
                        questionary.text(
                            f"Enter the elementId '{f}' replaces", validate=valid_id
                        ).unsafe_ask()
                    )

                    if use_params and not use_single_params_set:
                        params.append(
                            questionary.text(
                                f"Enter the parameters '{f}' takes separated by comma", validate=valid_js_params
                            ).unsafe_ask()
                        )

            onload_prop = questionary.confirm(
                "Would you like to add DOMContentLoaded listener event to every component?", default=False
            ).skip_if(behavior_prop == "return", default=False).unsafe_ask()

            watch_files = questionary.confirm(
                "Would you like PyWST to automatically refresh files on change?", default=False
            ).unsafe_ask()

            minify_files = questionary.confirm(
                "Would you like PyWST to minify (compact) all generated files?", default=True
            ).unsafe_ask()

            config_names.append(new_config)

            config_file.write(f"[{new_config}]\n")
            config_file.write(f"PATH = {files_path}\n")
            if not repl_id:
                for f in files:
                    config_file.write(f"FILE = {f}\n")
            elif not use_params:
                for f, _id in zip(files, repl_id):
                    config_file.write(f"FILE = {f}\n")
                    config_file.write(f"REPL_ID = {_id}\n")
            else:
                for f, _id, param in zip(files, repl_id, params):
                    config_file.write(f"FILE = {f}\n")
                    config_file.write(f"REPL_ID = {_id}\n")
                    config_file.write(f"PARAMS = {param}\n")

            config_file.write(f"BEHAVIOR = {behavior_prop}\n")

            if un_repl_id is not None:
                config_file.write(f"UN_REPL_ID = {un_repl_id}\n")
            if single_params is not None:
                config_file.write(f"PARAMS = {single_params}\n")

            config_file.write(f"ONLOAD = {onload_prop}\n")
            config_file.write(f"WATCH = {watch_files}\n")
            config_file.write(f"MINIFY_CODE = {minify_files}\n\n")
            config_file.flush()
            configurations_written += 1

            logging.info("Configuration saved")

            create_config = questionary.confirm(
                "Would you like to add another configuration?", default=False
            ).unsafe_ask()
        except KeyboardInterrupt:
            break

    config_file.close()

    if configurations_written == 0:
        logging.info(f"No data was written. Discarding '{config_file_path.name}'...")
        config_file_path.unlink(True)
        exit(1)
