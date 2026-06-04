import sys

from .converter import convert, to_wolfram


def main():
    args = sys.argv[1:]
    if not args:
        _usage()
        sys.exit(1)

    wolfram_mode = False
    fmt = "pretty"
    filename = None
    positional: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-f" or arg == "--file":
            i += 1
            if i >= len(args):
                print("Error: -f/--file requires a filename", file=sys.stderr)
                sys.exit(1)
            filename = args[i]
        elif arg == "--wolfram":
            wolfram_mode = True
        elif arg == "--plain":
            fmt = "plain"
        elif arg == "--latex":
            fmt = "latex"
        elif arg == "-h" or arg == "--help":
            _usage()
            sys.exit(0)
        else:
            positional.append(arg)
        i += 1

    expr = " ".join(positional) if positional else None

    if filename is not None:
        _process_file(filename, wolfram_mode, fmt)
    elif expr is not None:
        _process_expr(expr, wolfram_mode, fmt)
    else:
        _usage()
        sys.exit(1)


def _process_expr(expr: str, wolfram_mode: bool, fmt: str):
    try:
        if wolfram_mode:
            print(to_wolfram(expr))
        else:
            print(convert(expr, fmt=fmt))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _process_file(filename: str, wolfram_mode: bool, fmt: str):
    try:
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if wolfram_mode:
                        print(to_wolfram(line))
                    else:
                        print(convert(line, fmt=fmt))
    except FileNotFoundError:
        print(f"Error: file not found: {filename}", file=sys.stderr)
        sys.exit(1)


def _usage():
    print(
        "Usage: python -m mathio [--wolfram] [--plain|--latex] <expression>\n"
        "       python -m mathio [--wolfram] [--plain|--latex] -f <file>\n"
        "\n"
        "  --wolfram   Generate Wolfram Language code (default: evaluate with SymPy)\n"
        "  --plain     Plain text output (default: Unicode pretty-printing)\n"
        "  --latex     LaTeX output (default: Unicode pretty-printing)\n"
        "  -f, --file  Read expressions from a file, one per line\n"
    )


if __name__ == "__main__":
    main()
