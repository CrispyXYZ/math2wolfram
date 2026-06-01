import sys

from .converter import convert, execute


def main():
    args = sys.argv[1:]
    if not args:
        _usage()
        sys.exit(1)

    execute_mode = False
    pretty = True
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
        elif arg == "--execute":
            execute_mode = True
        elif arg == "--plain":
            pretty = False
        elif arg == "-h" or arg == "--help":
            _usage()
            sys.exit(0)
        else:
            positional.append(arg)
        i += 1

    expr = " ".join(positional) if positional else None

    if filename is not None:
        _process_file(filename, execute_mode, pretty)
    elif expr is not None:
        _process_expr(expr, execute_mode, pretty)
    else:
        _usage()
        sys.exit(1)


def _process_expr(expr: str, execute_mode: bool, pretty: bool):
    try:
        if execute_mode:
            print(execute(expr, pretty=pretty))
        else:
            print(convert(expr))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _process_file(filename: str, execute_mode: bool, pretty: bool):
    try:
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if execute_mode:
                        print(execute(line, pretty=pretty))
                    else:
                        print(convert(line))
    except FileNotFoundError:
        print(f"Error: file not found: {filename}", file=sys.stderr)
        sys.exit(1)


def _usage():
    print(
        "Usage: python -m math2wolfram [--execute] [--plain] <expression>\n"
        "       python -m math2wolfram [--execute] [--plain] -f <file>\n"
        "\n"
        "  --execute   Evaluate using SymPy (default: generate Wolfram code)\n"
        "  --plain     Use plain text output instead of Unicode pretty-printing\n"
        "              (only meaningful with --execute)\n"
        "  -f, --file  Read expressions from a file, one per line\n"
    )


if __name__ == "__main__":
    main()
