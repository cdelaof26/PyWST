
# This property will allow any character inside a closing tag.
# Normally, all closing tags should only include letters, digits and hyphens,
# however, in some cases the tag might contain whitespace characters.
#
ALLOW_ANYTHING_IN_CLOSE_TAGS = False

# Many dynamically generated webpages are missing a few closing tags,
# with this property on True any error will be omitted.
#
IGNORE_MISMATCHING_CLOSING_TAGS = False

# Minifying code will reduce file size and might improve load times
#
MINIFY_CODE = True


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
