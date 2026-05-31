from __future__ import annotations

from .config import CONST_MAP, FUNC_MAP, KEYWORD_TYPE
from .parser import Parser
from .tokenizer import Lexer
from .wolfram_generator import WolframGenerator


class Converter:
    def __init__(
        self,
        keyword_type: dict[str, str] | None = None,
        func_map: dict[str, str] | None = None,
        const_map: dict[str, str] | None = None,
    ):
        self._lexer = Lexer(keyword_type=keyword_type)
        self._parser = Parser()
        self._generator = WolframGenerator(func_map=func_map, const_map=const_map)
        self._keyword_type = keyword_type if keyword_type is not None else KEYWORD_TYPE

    def convert(self, source: str) -> str:
        tokens = self._lexer.tokenize(source)
        ast = self._parser.parse(tokens, source)
        return self._generator.generate(ast)


def convert(
    source: str,
    func_map: dict[str, str] | None = None,
    const_map: dict[str, str] | None = None,
) -> str:
    """Convenience function: convert a math expression to Wolfram Language."""
    return Converter(func_map=func_map, const_map=const_map).convert(source)
