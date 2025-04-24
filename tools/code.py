
indent = "    "


class Code:
    def __init__(self):
        self.source: list = list()
        self.indent_times = 0
        self.minify = False

    def append_line(self, line: str):
        if line.endswith("}") or line.startswith("}"):
            self.indent_times -= 1

        extra_newline = line.startswith("\n")
        if extra_newline:
            line = line[1:]

        self.source.append(("\n" if extra_newline else "") + f"{indent * self.indent_times}{line}")

        for struct in ["if", "for", "while", "function"]:
            # if not re.sub(struct + r" *?\(.+?\) *?{?.*?", "", line):
            if line.startswith(struct):
                self.indent_times += 1
                break
        else:
            if line.endswith("{"):
                self.indent_times += 1

    def append_all(self, lines: list[str]):
        for line in lines:
            self.append_line(line)

    def modify_indent(self, increase: bool):
        self.indent_times += 1 if increase else -1

    def __str__(self):
        if self.minify:
            min_source = []
            for line in self.source:
                if not line:
                    continue
                min_source.append(line.strip())

            return "".join(min_source)

        return "\n".join(self.source)
