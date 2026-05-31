# math2wolfram

Convert custom mathematical notation to valid Wolfram Language expressions.

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

- **Keyword splitting**: Reserved keywords (`sin`, `cos`, `tan`, `cot`, `sec`, `csc`, `log`, `ln`, `exp`, `int`, `d`, `pi`, `e`, `infty`) are split from adjacent identifiers via longest-prefix matching. For example: `sinx` → `sin` + `x`, `density` → `d` + `e` + `nsity`.
- **DERIV**: `d/dx`, `d/dy`, `d/dtheta` etc. are recognized as a single derivative token.
- **Numbers**: Integers, decimals, and scientific notation where `e` is immediately followed by a digit. `2e` is `2 * e`, `2e1` is `20`.
- **Unicode constants**: `π` and `∞` are recognized and mapped to `Pi` and `Infinity`.

## Examples

```python
from math2wolfram import convert

convert("sinx")              # Sin[x]
convert("sinπx")             # Sin[Times[Pi, x]]
convert("4x/3y")             # Times[Times[4, x], Power[Times[3, y], -1]]
convert("d/dx sinx cosx")    # D[Times[Sin[x], Cos[x]], x]
convert("int sinx d x")      # Integrate[Sin[x], x]
convert("int [1,2] sinx d x")  # Integrate[Sin[x], {x, 1, 2}]
convert("sin cos x y")       # Sin[Cos[Times[x, y]]]
convert("sin 2 x")           # Sin[Times[2, x]]
convert("sin x ^ 2")         # Power[Sin[x], 2]
```

## CLI Usage

```bash
python -m math2wolfram "sinx"
python -m math2wolfram -f expressions.txt
```

## Architecture

- `tokenizer.py` — Custom lexer with keyword splitting and DERIV detection
- `parser.py` — Recursive-descent parser producing AST
- `ast_nodes.py` — AST node dataclasses
- `wolfram_generator.py` — AST → Wolfram string (functional form)
- `converter.py` — Facade orchestrating the pipeline
- `config.py` — Function/constant/keyword mappings
- `errors.py` — Exception classes with source-context error messages
