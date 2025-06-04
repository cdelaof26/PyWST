from parsing.html_tokenize import HTMLTokenType, HTMLToken, tokenize_file, reset_html_tokenize
from parsing.html_tag import tokenize_html_token, TagToken, TagInfo, reset_html_tag_tokenize
from typing import Union, Optional
from tools.code import Code
from pathlib import Path
import utilities
import re

_id = 0
_html_entity_detected = False

# From http://xahlee.info/js/html5_non-closing_tag.html
SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"
]

LISTENERS = [
    "abort", "afterprint", "animationend", "animationiteration", "animationstart", "beforeprint", "beforeunload",
    "blur", "canplay", "canplaythrough", "change", "click", "contextmenu", "copy", "cut", "dblclick", "drag",
    "dragend", "dragenter", "dragleave", "dragover", "dragstart", "drop", "durationchange", "ended", "error", "focus",
    "focusin", "focusout", "fullscreenchange", "fullscreenerror", "hashchange", "input", "invalid", "keydown",
    "keypress", "keyup", "load", "loadeddata", "loadedmetadata", "loadstart", "message", "mousedown", "mouseenter",
    "mouseleave", "mousemove", "mouseover", "mouseout", "mouseup", "mousewheel", "offline", "online", "open",
    "pagehide", "pageshow", "paste", "pause", "play", "playing", "popstate", "progress", "ratechange", "resize",
    "reset", "scroll", "search", "seeked", "seeking", "select", "show", "stalled", "storage", "submit", "suspend",
    "timeupdate", "toggle", "touchcancel", "touchend", "touchmove", "touchstart", "transitionend", "unload",
    "volumechange", "waiting", "wheel"
]


def _filter_data_tokens(tokens: list[HTMLToken]) -> list:
    # Join all continuous DATA tokens and delete empty ones
    i = 0
    start = -1
    data_token = None
    while i < len(tokens):
        t: HTMLToken = tokens[i]
        if t.token_type != HTMLTokenType.DATA:
            if start == -1:
                t.lexeme = re.sub(r"\n+", " ", t.lexeme)
                i += 1
                continue

            data_token.lexeme = re.sub(r"^\n+", "", re.sub(r"\n+$", "", data_token.lexeme))
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

        data_token.lexeme += re.sub(r"^\t+", "", t.lexeme)
        i += 1

    return tokens


def _tokenize_tags(tokens: list):
    for i, token in enumerate(tokens):
        token_data = tokenize_html_token(tokens[i])
        if token_data:
            tokens[i] = token_data


def _get_js_name() -> str:
    global _id
    n = f"e{_id}"
    _id += 1
    return n


def create_js_element(name: str, tag: str, namespace_uri: Optional[str] = None) -> str:
    if namespace_uri is None:
        return f"const {name} = document.createElement('{tag}');"
    return f"const {name} = document.createElementNS({repr(namespace_uri)}, '{tag}');"


def set_boolean_property(name: str, tag_property: str) -> str:
    return f"{name}.setAttribute({repr(tag_property)}, true);"


def set_property(name: str, tag_property: str, params: bool = False) -> str:
    equal_position = tag_property.index("=")
    prop, value = tag_property[:equal_position], tag_property[equal_position + 1:]
    if value.startswith("{") or not value.startswith("'") and not value.startswith('"'):
        value = repr(value)

    if params and re.sub(r"\${.*?}", "", value) != value:
        value = f"`{value[1:-1]}`"

    if prop.startswith("on") and prop[2:] in LISTENERS:
        if value.startswith('"'):
            value = value[1:-1]
        return f"{name}.addEventListener('{prop[2:]}', (evt) => {value});"

    return f"{name}.setAttribute({repr(prop)}, {value});"


def tag_to_js(tag_data: list[TagToken], params: bool = False) -> tuple[str, str, list[str]]:
    if not tag_data:
        raise ValueError("tag_data cannot be empty")

    declared = False
    element_type = ""
    name = _get_js_name()
    js = []

    for d in tag_data:
        if d.data_type == TagInfo.TAG_NAME:
            if declared:  # This shouldn't happen if the input comes from translate_html
                raise ValueError(f"Can't create duplicate constant {name}")

            element_type = d.value.lower()
            if element_type in ["svg", "path"]:
                js.append(create_js_element(name, element_type, "http://www.w3.org/2000/svg"))
            else:
                js.append(create_js_element(name, element_type))

            declared = True
        elif d.data_type == TagInfo.ATTRIBUTE_NAME:
            js.append(set_boolean_property(name, d.value))
        else:
            js.append(set_property(name, d.value, params))

    if not declared:
        raise ValueError("A tag name is required")

    return name, element_type, js


def append_child(parent: str, child: str) -> str:
    return f"{parent}.appendChild({child});"


def append_text(name: str, value: str, params: bool = False) -> str:
    global _html_entity_detected

    value = repr(value)

    if params and re.sub(r"\${.*?}", "", value) != value:
        value = f"`{value[1:-1]}`"

    if utilities.AUTOMATICALLY_DECODE_HTML_ENTITIES and re.findall("&.*?;", value):
        _html_entity_detected = True
        return f"{name}.appendChild(document.createTextNode(dec({value})));"

    return f"{name}.appendChild(document.createTextNode({value}));"


def _transcribe_to_js(
        file_name: str, tokens: list[Union[HTMLToken, list]],
        behavior: str = "", repl_id: Optional[list] = None, un_repl_id: str = "", onload: bool = False,
        params: Optional[list] = None
) -> Code:
    assert tokens

    if isinstance(tokens[0], HTMLToken):
        if tokens[0].token_type == HTMLTokenType.DATA and "DOCTYPE HTML" in tokens[0].lexeme.upper():
            tokens.pop(0)
        else:
            raise ValueError(f"Illegal start of source {tokens[0].lexeme}")

    defined_active_script = False
    defined_element_to_replace = False
    element_id = None

    js = Code()
    if params is None:
        js.append_line(f"function {file_name}()" " {")
    elif behavior == "return":
        js.append_line(f"function {file_name}({', '.join(params[0])})" " {")
    elif (repl_id is None or not repl_id[0]) and not un_repl_id:
        defined_active_script = True
        js.append_all([
            f"function {file_name}()" " {", "let currentScript;",
            "const htmlScripts = document.querySelectorAll('script');",
            "for (let __i = 0; __i < htmlScripts.length; __i++) " "{",
            f"if (/(.*[/\\\]{file_name}\\.js)|(^{file_name}\\.js)/g.test(htmlScripts[__i].src)) " "{",
            "currentScript = htmlScripts[__i];", "break;", "}", "}"
        ])

        for p in params[0]:
            js.append_line(f"const {p} = currentScript.getAttribute({repr(p)});")
    else:
        defined_element_to_replace = True
        js.append_line(f"function {file_name}()" " {")
        element_id = un_repl_id if un_repl_id != "" else repl_id[0]
        element_id = repr(element_id)
        js.append_line(f"const myElementToRepl = document.getElementById({element_id});")
        for p in params[0]:
            js.append_line(f"const {p} = myElementToRepl.getAttribute({repr(p)});")

    parent_stack = []
    tag_stack = []
    base_element = None
    base_tag = None
    parent_is_svg = False

    for token in tokens:
        if isinstance(token, list):
            element_js_name, tag, code = tag_to_js(token, params and params[0])
            js.append_all(code)

            if tag == "svg":
                parent_is_svg = True

            if parent_stack:
                js.append_line(append_child(parent_stack[-1], element_js_name))
            elif base_element is None:
                if tag in SELF_CLOSING_TAGS:
                    raise ValueError("A self-closing tag cannot be a base component")

                base_element = element_js_name
                base_tag = tag
            else:
                raise ReferenceError(f"Found two base components: initial '{base_tag}', second '{tag}'")

            if tag not in SELF_CLOSING_TAGS and tag != "path":
                # There are probably more problematic SVG tags
                parent_stack.append(element_js_name)
                tag_stack.append(tag)
            continue

        if token.token_type == HTMLTokenType.DATA:
            if re.sub(r"\W+", "", token.lexeme):
                js.append_line(append_text(parent_stack[-1], token.lexeme, params and params[0]))
            continue

        # HTMLTokenType.CLOSING_TAG
        tag = token.lexeme[2:-1].lower()

        # After some research, looks like there's no standard way for SVG to represent
        # self-closing tags and not self-closing tags (some can be both),
        # so any closing tag will be ignored as long as they are inside an SVG
        #
        if tag == "svg":
            parent_is_svg = False
            if "svg" in tag_stack:
                while tag_stack[-1] != "svg":
                    tag_stack.pop()
                    parent_stack.pop()

        if parent_is_svg:
            continue

        top = tag_stack.pop()
        if tag != top:
            if utilities.IGNORE_MISMATCHING_CLOSING_TAGS:
                tag_stack.append(top)
                continue

            raise ValueError(f"Found closing tag for '{tag}' but current tag is '{top}', line {token.line}")

        parent_stack.pop()

    if behavior == "return":
        js.append_line(f"return {base_element};")
    elif un_repl_id or repl_id[0]:
        if element_id is None:
            element_id = un_repl_id if un_repl_id != "" else repl_id[0]
            element_id = repr(element_id)

        js.append_line(f"{base_element}.setAttribute('id', {element_id});")
        if defined_element_to_replace:
            js.append_line(f"myElementToRepl.replaceWith({base_element});")
        else:
            js.append_line(f"document.getElementById({element_id}).replaceWith({base_element});")
    elif not defined_active_script:
        js.append_line(f"document.currentScript.replaceWith({base_element});")
    else:
        js.append_line(f"currentScript.replaceWith({base_element});")

    js.append_line("}")

    if utilities.AUTOMATICALLY_DECODE_HTML_ENTITIES and _html_entity_detected:
        # From https://stackoverflow.com/questions/6155595/how-do-i-convert-an-html-entity-number-into-a-character
        # -using-plain-javascript-o
        js.append_all(["function dec(data) {", "const e = document.createElement('p');",
                       "e.innerHTML = data;", "return e.innerHTML;", "}"])

    if onload:
        js.append_all([
            "if (document.readyState === 'loading') {",
            'document.addEventListener("DOMContentLoaded", () => ' f"{file_name}()" ");",
            "} else {", f"{file_name}();", "}"
        ])

    return js


def transcribe_html(_file: Path, config: Optional[dict] = None):
    global _id, _html_entity_detected

    if config is not None:
        required = ["BEHAVIOR", "REPL_ID", "UN_REPL_ID", "ONLOAD", "PARAMS"]
        config = {key.lower(): value for key, value in config.items() if key in required}
    else:
        config = {"behavior": "return", "repl_id": [], "un_repl_id": "", "onload": False, "params": []}

    _id = 0
    _html_entity_detected = False
    name = _file.name
    if "." in name:
        name = name[:name.index(".")]
    name = name.replace("-", "_").replace(" ", "_")

    reset_html_tokenize()
    reset_html_tag_tokenize()

    with open(_file, "r") as f:
        data = f.readlines()
        tokens = tokenize_file(data)
        tokens = _filter_data_tokens(tokens)
        _tokenize_tags(tokens)
        return _transcribe_to_js(name, tokens, **config)
