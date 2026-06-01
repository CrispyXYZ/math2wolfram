from __future__ import annotations

from typing import Any

from . import ast_nodes as a
from .config import SYMPY_CONST_MAP, SYMPY_FUNC_MAP


class SymPyExecutor:
    def __init__(
        self,
        func_map: dict[str, str] | None = None,
        const_map: dict[str, str] | None = None,
    ):
        self._func_map = func_map if func_map is not None else SYMPY_FUNC_MAP
        self._const_map = const_map if const_map is not None else SYMPY_CONST_MAP

    def execute(self, node: a.Expr):
        """Walk *node* and return a ``sympy.Expr``."""
        import sympy

        return self._to_sympy(node, sympy)

    def evaluate(self, node: a.Expr, *, pretty: bool = True) -> str:
        result = self.execute(node)
        import sympy
        if pretty:
            return sympy.pretty(result, use_unicode=True)
        return str(result)

    # ── dispatch ──────────────────────────────────────────────────────

    def _to_sympy(self, node: a.Expr, sp: Any):
        if isinstance(node, a.Number):
            return _parse_exact_number(node.value, sp)
        if isinstance(node, a.Constant):
            attr = self._const_map.get(node.name, node.name)
            return getattr(sp, attr)
        if isinstance(node, a.Identifier):
            return sp.Symbol(node.name)
        if isinstance(node, a.BinaryOp):
            return self._binary(node, sp)
        if isinstance(node, a.ImplicitMultiply):
            factors = [self._to_sympy(f, sp) for f in node.factors]
            return sp.Mul(*factors)
        if isinstance(node, a.FuncCall):
            sp_func = getattr(sp, self._func_map.get(node.name, node.name))
            return sp_func(self._to_sympy(node.arg, sp))
        if isinstance(node, a.Integral):
            return sp.integrate(self._to_sympy(node.body, sp), sp.Symbol(node.var))
        if isinstance(node, a.DefiniteIntegral):
            return sp.integrate(
                self._to_sympy(node.body, sp),
                (sp.Symbol(node.var), self._to_sympy(node.lower, sp),
                 self._to_sympy(node.upper, sp)),
            )
        if isinstance(node, a.Derivative):
            return sp.diff(self._to_sympy(node.body, sp), sp.Symbol(node.var))
        if isinstance(node, a.Negation):
            return sp.Mul(sp.Integer(-1), self._to_sympy(node.expr, sp))
        raise TypeError(f"Unknown AST node: {type(node).__name__}")

    # ── binary ops ────────────────────────────────────────────────────

    def _binary(self, node: a.BinaryOp, sp: Any):
        left = self._to_sympy(node.left, sp)
        right = self._to_sympy(node.right, sp)
        if node.op == "+":
            return sp.Add(left, right)
        if node.op == "-":
            return sp.Add(left, sp.Mul(sp.Integer(-1), right))
        if node.op == "*":
            return sp.Mul(left, right)
        if node.op == "/":
            return sp.Mul(left, sp.Pow(right, sp.Integer(-1)))
        if node.op == "^":
            return sp.Pow(left, right)
        raise ValueError(f"Unknown binary operator: {node.op}")


# ── exact number parsing ──────────────────────────────────────────────

def _parse_exact_number(value: str, sp: Any):
    """Parse a number string into a sympy Integer or Rational, never Float."""
    low = value.lower()
    if "e" in low:
        mantissa_str, exp_str = low.split("e", 1)
        mantissa = _parse_exact_number(mantissa_str, sp)
        exponent = int(exp_str)
        return mantissa * sp.Pow(sp.Integer(10), sp.Integer(exponent))
    if "." in value:
        int_part, frac_part = value.split(".", 1)
        denominator = sp.Integer(10 ** len(frac_part))
        numerator = sp.Integer(int(int_part + frac_part))
        return sp.Rational(numerator, denominator)
    return sp.Integer(int(value))
