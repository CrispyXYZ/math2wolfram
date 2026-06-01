from __future__ import annotations

from .config import CONST_MAP, FUNC_MAP, KEYWORD_TYPE, SYMPY_CONST_MAP, SYMPY_FUNC_MAP
from .parser import Parser
from .sympy_executor import SymPyExecutor
from .tokenizer import Lexer
from .wolfram_generator import WolframGenerator


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

    def convert(self, source: str) -> str:
        tokens = self._lexer.tokenize(source)
        ast = self._parser.parse(tokens, source)
        return self._wolfram.generate(ast)

    def execute(self, source: str, *, pretty: bool = True) -> str:
        tokens = self._lexer.tokenize(source)
        ast = self._parser.parse(tokens, source)
        return self._sympy.evaluate(ast, pretty=pretty)


def convert(
    source: str,
    func_map: dict[str, str] | None = None,
    const_map: dict[str, str] | None = None,
) -> str:
    """Convenience function: convert a math expression to Wolfram Language."""
    return Converter(func_map=func_map, const_map=const_map).convert(source)


def execute(
    source: str,
    func_map: dict[str, str] | None = None,
    const_map: dict[str, str] | None = None,
    *,
    pretty: bool = True,
) -> str:
    """Evaluate a math expression symbolically using SymPy."""
    return Converter(
        sympy_func_map=func_map,
        sympy_const_map=const_map,
    ).execute(source, pretty=pretty)
