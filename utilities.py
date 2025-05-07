from argparse import Namespace
from typing import Optional
from pathlib import Path
import logging
import re

# Setting this property will allow any character inside a closing tag.
#
# Normally, all closing tags should only include letters, digits and hyphens,
# however, in some cases the tag might contain whitespace characters.
#
ALLOW_ANYTHING_IN_CLOSE_TAGS = False

# Many dynamically generated webpages are missing a few closing tags,
# with this option on, any error will be ignored.
#
# Enabling this property might cause incorrect results.
#
IGNORE_MISMATCHING_CLOSING_TAGS = False

# Some pages (mostly old) might include HTML entities to represent
# UTF-8 characters such as &pound; (£). Setting this property to True will
# create a function to automatically decode HTML entities when detected.
#
# This depends on the web browser character rendering capabilities.
#
AUTOMATICALLY_DECODE_HTML_ENTITIES = True

# Minifying code will reduce file size by removing new lines and indentation.
#
# Might improve load times with bigger files.
#
MINIFY_CODE = True


_PROPERTIES = {
    "ALLOW_ANYTHING_IN_CLOSE_TAGS": False,
    "IGNORE_MISMATCHING_CLOSING_TAGS": False,
    "AUTOMATICALLY_DECODE_HTML_ENTITIES": True,
    "MINIFY_CODE": True
}


def _set_property(n: int, b: bool):
    global ALLOW_ANYTHING_IN_CLOSE_TAGS, IGNORE_MISMATCHING_CLOSING_TAGS
    global AUTOMATICALLY_DECODE_HTML_ENTITIES, MINIFY_CODE

    if n == 0:
        ALLOW_ANYTHING_IN_CLOSE_TAGS = b
    elif n == 1:
        IGNORE_MISMATCHING_CLOSING_TAGS = b
    elif n == 2:
        AUTOMATICALLY_DECODE_HTML_ENTITIES = b
    else:
        MINIFY_CODE = b


def update_properties(data_block: dict):
    for i, name_default in enumerate(_PROPERTIES.items()):
        name, default = name_default
        _set_property(i, data_block[name] if name in data_block else default)


def remove_whitespace(data: str) -> str:
    for sequence in ["\t", "\n", "\r", "\b", "\f"]:
        data = data.replace(sequence, " ")
    return data


def raise_error(data: str, c: str, i: int, line: int = -1):
    data = remove_whitespace(data)
    c = repr(c)

    ex = f"Illegal character {c}, col {i}"

    if i > 49:
        data = "... " + data[i - 25:i + 25] + " ..."
        i = 29

    if line != -1:
        ex += f", line {line}\n"
        spacing = " " * len(str(line))
        ex += f"  {line}  {data}" + f"\n  {spacing}  " + "-" * (i - 1) + "^"
    else:
        ex += f"\n    {data}" + f"\n    " + "-" * (i - 1) + "^"

    raise ValueError(ex)


def list_html_files(initial_dir: Path) -> list[Path]:
    if not initial_dir.is_dir():
        return []

    directories = [initial_dir]
    files = []
    while directories:
        directory = directories.pop(0)
        for element in directory.iterdir():
            if element.is_file() and element.suffix.lower() == ".html":
                files.append(element)
            elif element.is_dir():
                directories.append(element)

    return files


def _verify_name(name: str):
    if name and not re.sub(r".+", "", name) and name[-1] == "]":
        return

    raise ValueError(f"Invalid block name '{name}'")


def _valid_js_params(_params: str) -> tuple[list, bool]:
    _params = _params.strip()
    if not _params:
        return [], True

    split = _params.split(",")
    params = []
    for p in split:
        p = p.strip()
        if not p or re.sub(r"[a-zA-Z_]\w+", "", p):
            return [], False
        params.append(p)

    return params, True


def _verify_property(prop_value: str, data: dict) -> any:
    equal_index = prop_value.index("=")
    prop, value = prop_value[:equal_index].strip(), prop_value[equal_index + 1:].strip()

    if prop not in ["FILE", "REPL_ID"] and prop in data:
        raise ValueError(f"Duplicated key '{prop}'")

    if prop == "BEHAVIOR":
        if value not in ["return", "replace"]:
            raise ValueError(f"Invalid value '{value}' for BEHAVIOR in {data['NAME']}")

        return value
    elif prop == "PATH":
        p = Path(value)
        if not p.exists() or not p.is_dir():
            raise ValueError(f"Specified PATH is not a directory or doesn't exist in {data['NAME']}\n    {p}")

        return p.resolve()
    elif prop == "FILE":
        if value == "*":
            if data['BEHAVIOR'] == "return" or "UN_REPL_ID" in data:
                return value

            raise ValueError(f"FILE = * is not allowed with behavior = replace or undefined UN_REPL_ID property "
                             f"for {data['NAME']}")

        p = data['PATH']
        f = Path(value)
        if f.exists() and f.is_file():
            return f.resolve()

        f = p.joinpath(value)
        if f.exists() and f.is_file():
            return f.resolve()

        raise ValueError(f"Specified FILE is not a file or doesn't exist in {data['NAME']}\n    {value}")
    elif prop == "REPL_ID" or prop == "UN_REPL_ID":
        if data['BEHAVIOR'] == "return":
            raise ValueError(f"REPL_ID or UN_REPL_ID cannot be used with BEHAVIOR = return for {data['NAME']}")

        if prop == "REPL_ID" and not value:
            return value

        if value and re.sub(r"[a-zA-Z][\w.:_-]+", "", value) == "":
            return value

        raise ValueError(f"Invalid REPL_ID or UN_REPL_ID value '{value}' for {data['NAME']}")

    elif prop == "PARAMS":
        parameters, valid = _valid_js_params(value)
        if not valid:
            raise ValueError(f"Specified JS parameters ({value}) are invalid in {data['NAME']}")

        return parameters

    if value.lower() in ["true", "false"]:
        return value.lower() == "true"

    raise ValueError(f"Invalid value '{value}' for {data['NAME']}")


def _parse_block(block) -> dict:
    data = {"NAME": re.findall(r"\[.+]", block)[0]}

    path = re.findall(r"PATH ?= ?.+", block)
    if len(path) != 1:
        raise ValueError(f"Missing PATH property or found multiple definitions for {data['NAME']}")
    data["PATH"] = _verify_property(path[0], data)

    behavior = re.findall("BEHAVIOR ?= ?.+", block)
    if not behavior:
        raise ValueError(f"Missing BEHAVIOR property for {data['NAME']}")
    data["BEHAVIOR"] = _verify_property(behavior[0], data)

    un_repl_id = re.findall("UN_REPL_ID ?= ?.+", block)
    if un_repl_id:
        data["UN_REPL_ID"] = _verify_property(un_repl_id[0], data)

    files = re.findall("FILE ?= ?.+", block)
    if not files:
        raise ValueError(f"Missing FILE property for {data['NAME']}")
    data["FILE"] = "*" if files[0][-1] == "*" else [_verify_property(f, data) for f in files]

    block = re.sub("UN_REPL_ID ?= ?.+", "", block)
    repl_id = re.findall("REPL_ID ?= ?.*", block)
    files_l, repl_id_l = len(files), len(repl_id)
    if repl_id:
        if "UN_REPL_ID" in data:
            raise ValueError(f"REPL_ID cannot be use with UN_REPL_ID. Problem found in {data['NAME']}")
        if files_l < repl_id_l:
            raise ValueError(f"Too few FILE properties in {data['NAME']} (FILE={files_l}, REPL_ID={repl_id_l})")
        if files_l > repl_id_l:
            raise ValueError(f"Too few REPL_ID properties in {data['NAME']} (FILE={files_l}, REPL_ID={repl_id_l})")

        data["REPL_ID"] = [_verify_property(r, data) for r in repl_id]
    elif data["BEHAVIOR"] == "replace" and "UN_REPL_ID" not in data:
        raise ValueError(f"BEHAVIOR = replace requires a REPL_ID for every FILE "
                         f"or UN_REPL_ID must have a value in {data['NAME']}")

    params = re.findall("PARAMS ?= ?.*", block)
    if params:
        data["PARAMS"] = [_verify_property(p, data) for p in params]
        params_l = len(params)
        if params_l != 1:
            if files_l < params_l:
                raise ValueError(f"Too few FILE properties in {data['NAME']} (FILE={files_l}, PARAMS={params_l})")
            if files_l > params_l:
                raise ValueError(f"Too few PARAMS properties in {data['NAME']} (FILE={files_l}, PARAMS={params_l})")
        elif params_l == 1:
            logging.info(f"All FILE will use the specified PARAMS in {data['NAME']}")

    for prop in ["ONLOAD", "WATCH", "MINIFY_CODE", "ALLOW_ANYTHING_IN_CLOSE_TAGS",
                 "IGNORE_MISMATCHING_CLOSING_TAGS", "AUTOMATICALLY_DECODE_HTML_ENTITIES"]:
        found = re.findall(f"{prop} ?= ?.+", block)
        if found:
            data[prop] = _verify_property(found[0], data)

    if "ONLOAD" in data and data["ONLOAD"] and data["BEHAVIOR"] == "return":
        raise ValueError(f"ONLOAD = True cannot be used with BEHAVIOR = return for {data['NAME']}")

    return data


def parse_config(_file: Path) -> list[dict]:
    with open(_file, "r") as f:
        data = f.read()

    config_blocks = []
    data = re.sub(r"#.*\n", "", data)
    data = data.split("\n")

    for line in data:
        if not line:
            continue

        if line.startswith("["):
            _verify_name(line)
            config_blocks.append(line)
            continue

        if not config_blocks:
            raise ValueError("Missing block name")

        config_blocks[-1] += f"\n{line}"

    if not config_blocks:
        raise ValueError("No data")

    return [_parse_block(block) for block in config_blocks]


def args_to_config(args: Namespace) -> Optional[dict]:
    config_block = "[ConfigArgs]\n"

    file0 = Path(args.file[0])

    if len(args.file) == 1 and file0.is_dir():
        config_block += f"PATH = {file0.resolve()}\n"
        config_block += f"FILE = *\n"
    else:
        config_block += "PATH = .\n"
        for str_f in args.file:
            f = Path(str_f)
            if f.is_dir():
                raise ValueError("You may specify either a directory or multiple files but not both")

            config_block += f"FILE = {str_f}\n"

    if args.idrepl is not None:
        for repl in args.idrepl:
            config_block += f"REPL_ID = {repl}\n"

    args.behavior = "return" if args.behavior == "ret" else "replace"
    config_block += f"BEHAVIOR = {args.behavior}\n"

    options = [
        args.uidrepl, args.params, args.onload, args.watch, args.minify, args.ictag,
        args.mctag, args.entdec
    ]
    config_options = [
        "UN_REPL_ID", "PARAMS", "ONLOAD", "WATCH", "MINIFY_CODE", "ALLOW_ANYTHING_IN_CLOSE_TAGS",
        "IGNORE_MISMATCHING_CLOSING_TAGS", "AUTOMATICALLY_DECODE_HTML_ENTITIES"
    ]

    for option, config_option in zip(options, config_options):
        if option is None:
            continue

        if option == "yes":
            option = "True"
        elif option == "no":
            option = "False"

        config_block += f"{config_option} = {option}\n"

    # print(config_block)

    return _parse_block(config_block)
