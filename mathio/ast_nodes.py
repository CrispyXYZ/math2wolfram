from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class Number:
    value: str  # raw token text, e.g. "2.5", "3", "1e-10"


@dataclasses.dataclass(frozen=True)
class Constant:
    name: str  # "pi", "e", "infty"


@dataclasses.dataclass(frozen=True)
class Identifier:
    name: str


@dataclasses.dataclass(frozen=True)
class BinaryOp:
    op: str  # "+", "-", "*", "/", "^"
    left: Expr
    right: Expr


@dataclasses.dataclass(frozen=True)
class ImplicitMultiply:
    factors: list[Expr]


@dataclasses.dataclass(frozen=True)
class FuncCall:
    name: str  # e.g. "sin", "cos"
    arg: Expr


@dataclasses.dataclass(frozen=True)
class Integral:
    var: str
    body: Expr


@dataclasses.dataclass(frozen=True)
class DefiniteIntegral:
    var: str
    body: Expr
    lower: Expr
    upper: Expr


@dataclasses.dataclass(frozen=True)
class Derivative:
    var: str
    body: Expr


@dataclasses.dataclass(frozen=True)
class Negation:
    expr: Expr


Expr = (
    Number
    | Constant
    | Identifier
    | BinaryOp
    | ImplicitMultiply
    | FuncCall
    | Integral
    | DefiniteIntegral
    | Derivative
    | Negation
)
