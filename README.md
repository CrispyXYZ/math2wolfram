# mathio

Parse custom mathematical notation and evaluate symbolically with [SymPy](https://www.sympy.org/). Also supports generating Wolfram Language code as an opt-in backend.

## Installation

```bash
pip install mathio
```

SymPy is installed automatically as a required dependency.

## Quick Start

```python
from mathio import convert, to_wolfram

# Evaluate symbolically (default)
convert("sin(π/4)")          # Unicode pretty-print
convert("sin(π/4)", fmt="plain")  # "sqrt(2)/2"
convert("sin(π/4)", fmt="latex")  # "\frac{\sqrt{2}}{2}"

# Generate Wolfram Language code
to_wolfram("sinx")           # "Sin[x]"
to_wolfram("int sinx d x")   # "Integrate[Sin[x], x]"
```

## CLI Usage

```bash
python -m mathio "sin(π/4)"             # SymPy evaluation (pretty)
python -m mathio --plain "sin(π/4)"     # SymPy (plain text)
python -m mathio --latex "sin(π/4)"     # SymPy (LaTeX)
python -m mathio --wolfram "sinx"       # Wolfram Language code
python -m mathio --wolfram -f input.txt # Batch Wolfram generation
```

## Grammar

```
expression      : add_expr
add_expr        : mul_expr (('+'|'-') mul_expr)*
mul_expr        : power_expr (('*'|'/') power_expr)*
power_expr      : implicit_mul ('^' power_expr)?        (right-associative)
implicit_mul    : factor+                                (n-ary, left-associative)
factor          : integral | derivative | func_app | unary_minus | atom
integral        : 'int' ('[' expression ',' expression ']')? expression 'd' IDENT
derivative      : DERIV implicit_mul
func_app        : FUNC '(' expression ')'
                | FUNC implicit_mul                       (stops at next FUNC)
unary_minus     : '-' factor
atom            : NUMBER | CONSTANT | IDENT | '(' expression ')'
```

## Lexical Rules

- **Keyword splitting**: Reserved keywords are split from adjacent identifiers via longest-prefix matching. e.g. `sinx` → `sin` + `x`, `density` → `d` + `e` + `nsity`.
- **DERIV**: `d/dx`, `d/dy`, `d/dtheta` are recognized as a single derivative token.
- **Numbers**: Integers, decimals, and scientific notation. The `e` in `2e1` is scientific notation; `2e` is `2 * e`.
- **Unicode constants**: `π` → `pi`, `∞` → `infty`.

## More Examples

```python
from mathio import convert, to_wolfram

# SymPy evaluation
convert("sinx")                   # sin(x)
convert("int sinx d x")           # -cos(x)
convert("d/dx sinx")              # cos(x)
convert("int [0,1] x d x")        # 1/2
convert("2^10")                   # 1024
convert("1/3 + 1/6")              # 1/2

# Wolfram generation
to_wolfram("sinπx")               # Sin[Times[Pi, x]]
to_wolfram("4x/3y")               # Times[Times[4, x], Power[Times[3, y], -1]]
to_wolfram("d/dx sinx cosx")      # D[Times[Sin[x], Cos[x]], x]
to_wolfram("sin cos x y")         # Sin[Cos[Times[x, y]]]
to_wolfram("sin x ^ 2")           # Power[Sin[x], 2]
```

## Architecture

```
mathio/
    tokenizer.py          # Custom lexer with keyword splitting & DERIV
    parser.py             # Recursive-descent parser → AST
    ast_nodes.py          # AST node dataclasses
    sympy_executor.py     # AST → SymPy evaluation (default backend)
    wolfram_generator.py  # AST → Wolfram Language code (opt-in)
    converter.py          # Facade: tokenize → parse → execute/generate
    config.py             # Function/constant/keyword mappings
    errors.py             # Exception classes with source-context errors
    __main__.py           # CLI entry point
```
