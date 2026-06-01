# Token types produced by the lexer for each reserved keyword.
# Keys: reserved keywords (sorted longest-first for greedy matching).
# Values: token type string.
KEYWORD_TYPE: dict[str, str] = {
    "infty": "CONSTANT",
    "sin": "FUNC",
    "cos": "FUNC",
    "tan": "FUNC",
    "cot": "FUNC",
    "sec": "FUNC",
    "csc": "FUNC",
    "log": "FUNC",
    "ln": "FUNC",
    "exp": "FUNC",
    "int": "INT",
    "pi": "CONSTANT",
    "e": "CONSTANT",
    "d": "DIFF",
}

# Mapping from input function name → Wolfram function name.
FUNC_MAP: dict[str, str] = {
    "sin": "Sin",
    "cos": "Cos",
    "tan": "Tan",
    "cot": "Cot",
    "sec": "Sec",
    "csc": "Csc",
    "log": "Log",
    "ln": "Log",
    "exp": "Exp",
}

# Mapping from input constant name → Wolfram constant expression.
CONST_MAP: dict[str, str] = {
    "pi": "Pi",
    "e": "E",
    "infty": "Infinity",
}

# All keywords that participate in identifier splitting, sorted longest-first.
KEYWORDS_BY_LENGTH: list[str] = sorted(KEYWORD_TYPE.keys(), key=len, reverse=True)

# Mapping from input function name → SymPy function attribute name.
SYMPY_FUNC_MAP: dict[str, str] = {
    "sin": "sin",
    "cos": "cos",
    "tan": "tan",
    "cot": "cot",
    "sec": "sec",
    "csc": "csc",
    "log": "log",
    "ln": "log",
    "exp": "exp",
}

# Mapping from input constant name → SymPy constant attribute name.
SYMPY_CONST_MAP: dict[str, str] = {
    "pi": "pi",
    "e": "E",
    "infty": "oo",
}
