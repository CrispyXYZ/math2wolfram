from __future__ import annotations

import dataclasses
import re

from .config import KEYWORD_TYPE
from .errors import LexerError


@dataclasses.dataclass(frozen=True)
class Token:
    type: str
    value: str
    start: int
    end: int


class Lexer:
    def __init__(self, keyword_type: dict[str, str] | None = None):
        self._keyword_type = keyword_type if keyword_type is not None else KEYWORD_TYPE
        self._keywords_by_len = sorted(self._keyword_type.keys(), key=len, reverse=True)
        self._source: str = ""
        self._pos: int = 0
        self._buffer: list[Token] = []

    def tokenize(self, source: str) -> list[Token]:
        self._source = source
        self._pos = 0
        self._buffer = []
        tokens: list[Token] = []
        while True:
            # Drain buffered sub-tokens first (from keyword splitting).
            tok = self._next_from_buffer()
            if tok is not None:
                tokens.append(tok)
                continue
            if self._pos >= len(self._source):
                break
            ch = self._source[self._pos]
            if ch.isspace():
                self._pos += 1
                continue
            tok = (
                self._try_deriv()
                or self._try_operator()
                or self._try_bracket_or_comma()
                or self._try_number()
                or self._try_unicode_constant()
                or self._try_identifier()
            )
            if tok is None:
                raise LexerError(
                    f"Unexpected character '{ch}'",
                    self._source,
                    self._pos,
                )
            tokens.append(tok)
        return tokens

    # ── buffer ─────────────────────────────────────────────────────────

    def _next_from_buffer(self) -> Token | None:
        if self._buffer:
            return self._buffer.pop(0)
        return None

    # ── DERIV  d/dx  d/dtheta ──────────────────────────────────────────

    def _try_deriv(self) -> Token | None:
        # Match d/d{var} where var is [a-zA-Z]+.
        if not self._source.startswith("d/", self._pos):
            return None
        j = self._pos + 2  # after "d/"
        if j >= len(self._source):
            return None
        # The character right after "d/" is the Leibniz 'd' (as in d/dx).
        # Skip it to get to the variable name.
        if self._source[j] == 'd':
            j += 1
        if j >= len(self._source) or not self._source[j].isalpha():
            return None
        var_start = j
        while j < len(self._source) and self._source[j].isalpha():
            j += 1
        var = self._source[var_start:j]
        tok = Token("DERIV", var, self._pos, j)
        self._pos = j
        return tok

    # ── operators ─────────────────────────────────────────────────────

    _OPERATORS: dict[str, str] = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "TIMES",
        "/": "DIVIDE",
        "^": "POWER",
    }

    def _try_operator(self) -> Token | None:
        ch = self._source[self._pos]
        if ch in self._OPERATORS:
            self._pos += 1
            return Token(self._OPERATORS[ch], ch, self._pos - 1, self._pos)
        return None

    # ── brackets / comma ──────────────────────────────────────────────

    _BRACKETS: dict[str, str] = {
        "(": "LPAREN",
        ")": "RPAREN",
        "[": "LBRACKET",
        "]": "RBRACKET",
    }

    def _try_bracket_or_comma(self) -> Token | None:
        ch = self._source[self._pos]
        if ch in self._BRACKETS:
            self._pos += 1
            return Token(self._BRACKETS[ch], ch, self._pos - 1, self._pos)
        if ch == ",":
            self._pos += 1
            return Token("COMMA", ",", self._pos - 1, self._pos)
        return None

    # ── number ────────────────────────────────────────────────────────

    # e must be followed by a digit to count as scientific notation.
    _NUMBER_RE = re.compile(r"\d+(?:\.\d+)?(?:[eE]\d+)?")

    def _try_number(self) -> Token | None:
        ch = self._source[self._pos]
        if not ch.isdigit():
            return None
        m = self._NUMBER_RE.match(self._source, self._pos)
        if m is None:
            return None
        value = m.group()
        tok = Token("NUMBER", value, self._pos, self._pos + len(value))
        self._pos += len(value)
        return tok

    # ── identifier / keyword splitting ────────────────────────────────

    _UNICODE_CONSTANTS: dict[str, str] = {
        "π": "pi",     # π
        "∞": "infty",  # ∞
    }

    def _try_identifier(self) -> Token | None:
        ch = self._source[self._pos]
        if not ch.isalpha() or ch in self._UNICODE_CONSTANTS:
            return None
        # Scan the full contiguous ASCII-letter sequence.
        start = self._pos
        while (
            self._pos < len(self._source)
            and self._source[self._pos].isalpha()
            and self._source[self._pos] not in self._UNICODE_CONSTANTS
        ):
            self._pos += 1
        word = self._source[start:self._pos]
        subtokens = self._split_word(word, start)
        if len(subtokens) == 1:
            return subtokens[0]
        # Multiple sub-tokens: return the first, buffer the rest.
        self._buffer = subtokens[1:]
        return subtokens[0]

    def _try_unicode_constant(self) -> Token | None:
        ch = self._source[self._pos]
        if ch in self._UNICODE_CONSTANTS:
            name = self._UNICODE_CONSTANTS[ch]
            self._pos += 1
            return Token("CONSTANT", name, self._pos - 1, self._pos)
        return None

    def _split_word(self, word: str, base_offset: int) -> list[Token]:
        """Split *word* using greedy longest-keyword-prefix matching."""
        tokens: list[Token] = []
        i = 0
        while i < len(word):
            kw = self._longest_keyword_prefix(word, i)
            if kw is not None:
                ttype = self._keyword_type[kw]
                tokens.append(Token(ttype, kw, base_offset + i, base_offset + i + len(kw)))
                i += len(kw)
            else:
                seg_start = i
                i += 1
                while i < len(word) and self._longest_keyword_prefix(word, i) is None:
                    i += 1
                tokens.append(Token("IDENT", word[seg_start:i],
                                    base_offset + seg_start, base_offset + i))
        return tokens

    def _longest_keyword_prefix(self, word: str, start: int) -> str | None:
        for kw in self._keywords_by_len:
            if word.startswith(kw, start):
                return kw
        return None
