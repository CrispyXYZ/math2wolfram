import sys

from .converter import convert


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python -m math2wolfram <expression>  or  python -m math2wolfram -f <file>")
        sys.exit(1)
    if args[0] == "-f" or args[0] == "--file":
        if len(args) < 2:
            print("Error: -f/--file requires a filename", file=sys.stderr)
            sys.exit(1)
        with open(args[1]) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    print(convert(line))
    else:
        expr = " ".join(args)
        print(convert(expr))


if __name__ == "__main__":
    main()
