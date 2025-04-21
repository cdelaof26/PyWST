
def escape_whitespace(data: str) -> str:
    for sequence, repl in zip(["\t", "\n", "\r", "\b", "\f"], ["\\t", "\\n", "\\r", "\\b", "\\f"]):
        data = data.replace(sequence, repl)
    return data


def remove_whitespace(data: str) -> str:
    for sequence in ["\t", "\n", "\r", "\b", "\f"]:
        data = data.replace(sequence, " ")
    return data


def raise_error(data: str, c: str, i: int, line: int = -1):
    data = remove_whitespace(data)
    c = escape_whitespace(c)

    ex = f"Illegal character '{c}', char.no {i}"
    if line != -1:
        ex += f", line {line}\n"
        spacing = " " * len(str(line))
        ex += f"  {line}  {data}" + f"\n  {spacing}  " + "-" * (i - 1) + "^"
    else:
        ex += f"\n    {data}" + f"\n    " + "-" * i + "^"

    raise ValueError(ex)
