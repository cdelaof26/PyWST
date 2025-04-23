
# This property will allow any character inside a closing tag.
#
# Normally, all closing tags should only include letters, digits and hyphens,
# however, in some cases the tag might contain whitespace characters.
#
# Setting this property to True will ignore those errors.
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
