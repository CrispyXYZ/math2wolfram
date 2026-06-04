from __future__ import annotations

from . import ast_nodes as a
from .config import CONST_MAP, FUNC_MAP


class WolframGenerator:
    def __init__(
        self,
        func_map: dict[str, str] | None = None,
        const_map: dict[str, str] | None = None,
    ):
        self._func_map = func_map if func_map is not None else FUNC_MAP
        self._const_map = const_map if const_map is not None else CONST_MAP

    def generate(self, node: a.Expr) -> str:
        if isinstance(node, a.Number):
            return node.value
        if isinstance(node, a.Constant):
            return self._const_map.get(node.name, node.name)
        if isinstance(node, a.Identifier):
            return node.name
        if isinstance(node, a.BinaryOp):
            left = self.generate(node.left)
            right = self.generate(node.right)
            if node.op == "+":
                return f"Plus[{left}, {right}]"
            if node.op == "-":
                return f"Subtract[{left}, {right}]"
            if node.op == "*":
                return f"Times[{left}, {right}]"
            if node.op == "/":
                return f"Times[{left}, Power[{right}, -1]]"
            if node.op == "^":
                return f"Power[{left}, {right}]"
            raise ValueError(f"Unknown binary operator: {node.op}")
        if isinstance(node, a.ImplicitMultiply):
            args = ", ".join(self.generate(f) for f in node.factors)
            return f"Times[{args}]"
        if isinstance(node, a.FuncCall):
            wl_name = self._func_map.get(node.name, node.name)
            return f"{wl_name}[{self.generate(node.arg)}]"
        if isinstance(node, a.Integral):
            return f"Integrate[{self.generate(node.body)}, {node.var}]"
        if isinstance(node, a.DefiniteIntegral):
            return (
                f"Integrate[{self.generate(node.body)}, "
                f"{{{node.var}, {self.generate(node.lower)}, {self.generate(node.upper)}}}]"
            )
        if isinstance(node, a.Derivative):
            return f"D[{self.generate(node.body)}, {node.var}]"
        if isinstance(node, a.Negation):
            return f"Times[-1, {self.generate(node.expr)}]"
        raise TypeError(f"Unknown AST node: {type(node).__name__}")
