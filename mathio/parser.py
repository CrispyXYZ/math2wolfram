from __future__ import annotations

from .ast_nodes import (
    BinaryOp,
    Constant,
    DefiniteIntegral,
    Derivative,
    Expr,
    FuncCall,
    Identifier,
    ImplicitMultiply,
    Integral,
    Negation,
    Number,
)
from .errors import ParseError
from .tokenizer import Token


class TokenStream:
    def __init__(self, tokens: list[Token], source: str):
        self._tokens = tokens
        self._source = source
        self._pos = 0

    def peek(self) -> Token | None:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def advance(self) -> Token:
        tok = self.peek()
        if tok is None:
            raise ParseError("Unexpected end of input", self._source, len(self._source), len(self._source))
        self._pos += 1
        return tok

    def expect(self, ttype: str) -> Token:
        tok = self.peek()
        if tok is None:
            raise ParseError(
                f"Expected {ttype_desc(ttype)} but reached end of input",
                self._source,
                len(self._source),
                len(self._source),
            )
        if tok.type != ttype:
            raise ParseError(
                f"Expected {ttype_desc(ttype)} but found {ttype_desc(tok.type)} '{tok.value}'",
                self._source,
                tok.start,
                tok.end,
            )
        return self.advance()

    def at_end(self) -> bool:
        return self._pos >= len(self._tokens)

    def __bool__(self):
        return not self.at_end()

    @property
    def source(self) -> str:
        return self._source


def ttype_desc(ttype: str) -> str:
    names: dict[str, str] = {
        "NUMBER": "a number",
        "CONSTANT": "a constant (pi, e, infty)",
        "IDENT": "an identifier",
        "FUNC": "a function name",
        "DIFF": "'d'",
        "INT": "'int'",
        "DERIV": "a derivative operator (d/dx, ...)",
        "LPAREN": "'('",
        "RPAREN": "')'",
        "LBRACKET": "'['",
        "RBRACKET": "']'",
        "COMMA": "','",
        "PLUS": "'+'",
        "MINUS": "'-'",
        "TIMES": "'*'",
        "DIVIDE": "'/'",
        "POWER": "'^'",
    }
    return names.get(ttype, ttype)


class Parser:
    def __init__(self):
        self._stream: TokenStream | None = None

    def parse(self, tokens: list[Token], source: str) -> Expr:
        self._stream = TokenStream(tokens, source)
        expr = self._parse_expression()
        if not self._stream.at_end():
            tok = self._stream.peek()
            raise ParseError(
                f"Unexpected token '{tok.value}'",
                self._stream.source,
                tok.start,
                tok.end,
            )
        return expr

    # ── expression ────────────────────────────────────────────────────

    def _parse_expression(self) -> Expr:
        return self._parse_add_expr()

    # ── add_expr : mul_expr (('+'|'-') mul_expr)* ─────────────────────

    def _parse_add_expr(self) -> Expr:
        left = self._parse_mul_expr()
        while True:
            tok = self._stream.peek()
            if tok is None or tok.type not in ("PLUS", "MINUS"):
                break
            op = self._stream.advance().value
            right = self._parse_mul_expr()
            left = BinaryOp(op, left, right)
        return left

    # ── mul_expr : power_expr (('*'|'/') power_expr)* ─────────────────

    def _parse_mul_expr(self) -> Expr:
        left = self._parse_power_expr()
        while True:
            tok = self._stream.peek()
            if tok is None or tok.type not in ("TIMES", "DIVIDE"):
                break
            op = self._stream.advance().value
            right = self._parse_power_expr()
            left = BinaryOp(op, left, right)
        return left

    # ── power_expr : implicit_mul ('^' power_expr)? ───────────────────

    def _parse_power_expr(self) -> Expr:
        left = self._parse_implicit_mul()
        tok = self._stream.peek()
        if tok is not None and tok.type == "POWER":
            self._stream.advance()
            right = self._parse_power_expr()  # right-associative
            left = BinaryOp("^", left, right)
        return left

    # ── implicit_mul : factor+ ────────────────────────────────────────

    def _parse_implicit_mul(self, stop_at_func: bool = False) -> Expr:
        """Parse one or more factors as implicit multiplication.

        When *stop_at_func* is True (used inside a function's implicit
        argument), subsequent factors are not consumed if they start with a
        FUNC token.  This prevents ``sin x cosx`` from being parsed as
        ``sin(x*cos(x))`` when the intent is ``sin(x) * cos(x)``.
        """
        factors = [self._parse_factor()]
        while self._can_start_factor():
            if stop_at_func and self._stream.peek().type == "FUNC":
                break
            factors.append(self._parse_factor())
        if len(factors) == 1:
            return factors[0]
        return ImplicitMultiply(factors)

    def _can_start_factor(self) -> bool:
        tok = self._stream.peek()
        if tok is None:
            return False
        return tok.type in {
            "INT",       # integral
            "DERIV",     # derivative
            "FUNC",      # func_app
            "NUMBER",    # atom
            "CONSTANT",  # atom
            "IDENT",     # atom
            "LPAREN",    # atom -> '(' expression ')'
        }

    # ── factor ────────────────────────────────────────────────────────

    def _parse_factor(self) -> Expr:
        tok = self._stream.peek()
        if tok is None:
            raise ParseError(
                "Unexpected end of input, expected an expression",
                self._stream.source,
                len(self._stream.source),
                len(self._stream.source),
            )
        if tok.type == "INT":
            return self._parse_integral()
        if tok.type == "DERIV":
            return self._parse_derivative()
        if tok.type == "FUNC":
            return self._parse_func_app()
        if tok.type == "MINUS":
            return self._parse_unary_minus()
        return self._parse_atom()

    # ── integral ──────────────────────────────────────────────────────

    def _parse_integral(self) -> Expr:
        self._stream.expect("INT")
        lower: Expr | None = None
        upper: Expr | None = None
        if self._stream.peek() is not None and self._stream.peek().type == "LBRACKET":
            self._stream.advance()  # [
            lower = self._parse_expression()
            self._stream.expect("COMMA")
            upper = self._parse_expression()
            self._stream.expect("RBRACKET")
        body = self._parse_expression()
        # The 'd' token terminates the integrand.
        diff_tok = self._stream.peek()
        if diff_tok is None or diff_tok.type != "DIFF":
            raise ParseError(
                "Expected 'd' followed by variable of integration (e.g., 'int expr d x')",
                self._stream.source,
                diff_tok.start if diff_tok else 0,
                diff_tok.end if diff_tok else 0,
            )
        self._stream.advance()  # consume DIFF
        var_tok = self._stream.peek()
        if var_tok is None or var_tok.type != "IDENT":
            raise ParseError(
                "Expected variable of integration after 'd' (e.g., 'd x')",
                self._stream.source,
                var_tok.start if var_tok else 0,
                var_tok.end if var_tok else 0,
            )
        self._stream.advance()  # consume IDENT
        var = var_tok.value
        if lower is not None:
            return DefiniteIntegral(var=var, body=body, lower=lower, upper=upper)
        return Integral(var=var, body=body)

    # ── derivative ────────────────────────────────────────────────────

    def _parse_derivative(self) -> Expr:
        tok = self._stream.expect("DERIV")
        body = self._parse_implicit_mul()
        return Derivative(var=tok.value, body=body)

    # ── func_app ──────────────────────────────────────────────────────

    def _parse_func_app(self) -> Expr:
        name = self._stream.expect("FUNC").value
        tok = self._stream.peek()
        if tok is not None and tok.type == "LPAREN":
            self._stream.advance()  # (
            arg = self._parse_expression()
            self._stream.expect("RPAREN")
        else:
            if not self._can_start_factor():
                raise ParseError(
                    f"Function '{name}' requires an argument",
                    self._stream.source,
                    tok.start if tok else 0,
                    tok.end if tok else 0,
                )
            arg = self._parse_implicit_mul(stop_at_func=True)
        return FuncCall(name=name, arg=arg)

    # ── unary_minus ───────────────────────────────────────────────────

    def _parse_unary_minus(self) -> Expr:
        self._stream.expect("MINUS")
        return Negation(expr=self._parse_factor())

    # ── atom ──────────────────────────────────────────────────────────

    def _parse_atom(self) -> Expr:
        tok = self._stream.advance()
        if tok.type == "NUMBER":
            return Number(value=tok.value)
        if tok.type == "CONSTANT":
            return Constant(name=tok.value)
        if tok.type == "IDENT":
            return Identifier(name=tok.value)
        if tok.type == "LPAREN":
            expr = self._parse_expression()
            self._stream.expect("RPAREN")
            return expr
        raise ParseError(
            f"Unexpected token '{tok.value}', expected an expression",
            self._stream.source,
            tok.start,
            tok.end,
        )
