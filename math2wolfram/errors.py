class BMWError(Exception):
    """Base exception for math2wolfram."""


class LexerError(BMWError):
    def __init__(self, message: str, source: str, pos: int):
        self.source = source
        self.pos = pos
        super().__init__(_format_error(message, source, pos, pos + 1))


class ParseError(BMWError):
    def __init__(self, message: str, source: str, start: int, end: int):
        self.source = source
        self.start = start
        self.end = end
        super().__init__(_format_error(message, source, start, end))


def _format_error(message: str, source: str, start: int, end: int) -> str:
    line_start = source.rfind("\n", 0, start) + 1
    line_end = source.find("\n", start)
    if line_end == -1:
        line_end = len(source)
    line = source[line_start:line_end]
    col_start = start - line_start
    col_end = end - line_start
    pointer = " " * col_start + "^" * max(col_end - col_start, 1)
    return f"{message}\n  {line}\n  {pointer}"
