from __future__ import annotations

from typing import Literal

from .config import CONST_MAP, FUNC_MAP, KEYWORD_TYPE, SYMPY_CONST_MAP, SYMPY_FUNC_MAP
from .parser import Parser
from .sympy_executor import SymPyExecutor
from .tokenizer import Lexer
from .wolfram_generator import WolframGenerator

Format = Literal["pretty", "plain", "latex"]


class Converter:
    def __init__(
        self,
        keyword_type: dict[str, str] | None = None,
        func_map: dict[str, str] | None = None,
        const_map: dict[str, str] | None = None,
        sympy_func_map: dict[str, str] | None = None,
        sympy_const_map: dict[str, str] | None = None,
    ):
        self._lexer = Lexer(keyword_type=keyword_type)
        self._parser = Parser()
        self._wolfram = WolframGenerator(func_map=func_map, const_map=const_map)
        self._sympy = SymPyExecutor(
            func_map=sympy_func_map if sympy_func_map is not None else SYMPY_FUNC_MAP,
            const_map=sympy_const_map if sympy_const_map is not None else SYMPY_CONST_MAP,
        )

    def convert(self, source: str, *, fmt: Format = "pretty") -> str:
        """Evaluate *source* symbolically using SymPy and return the result.

        *fmt* controls the output format:
        - ``"pretty"`` — Unicode pretty-printing (default)
        - ``"plain"`` — plain text
        - ``"latex"`` — LaTeX string
        """
        tokens = self._lexer.tokenize(source)
        ast = self._parser.parse(tokens, source)
        return self._sympy.evaluate(ast, fmt=fmt)

    def to_wolfram(self, source: str) -> str:
        """Generate Wolfram Language code for *source*."""
        tokens = self._lexer.tokenize(source)
        ast = self._parser.parse(tokens, source)
        return self._wolfram.generate(ast)


def convert(source: str, *, fmt: Format = "pretty") -> str:
    """Evaluate a mathematical expression symbolically using SymPy.

    Shortcut for ``Converter().convert(source, fmt=fmt)``.
    """
    return Converter().convert(source, fmt=fmt)


def to_wolfram(source: str) -> str:
    """Generate Wolfram Language code for a mathematical expression.

    Shortcut for ``Converter().to_wolfram(source)``.
    """
    return Converter().to_wolfram(source)
