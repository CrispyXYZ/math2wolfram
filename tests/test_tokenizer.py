import pytest
from math2wolfram.tokenizer import Lexer, Token
from math2wolfram.errors import LexerError


def token_types(tokens):
    return [(t.type, t.value) for t in tokens]


class TestKeywordSplitting:
    def setup_method(self):
        self.lexer = Lexer()

    def test_sinx_splits_to_func_ident(self):
        assert token_types(self.lexer.tokenize("sinx")) == [
            ("FUNC", "sin"), ("IDENT", "x")
        ]

    def test_density_splits_with_e_keyword(self):
        # With 'e' as a CONSTANT keyword, 'ensity' splits further.
        assert token_types(self.lexer.tokenize("density")) == [
            ("DIFF", "d"), ("CONSTANT", "e"), ("IDENT", "nsity")
        ]

    def test_dtheta_splits(self):
        assert token_types(self.lexer.tokenize("dtheta")) == [
            ("DIFF", "d"), ("IDENT", "th"), ("CONSTANT", "e"), ("IDENT", "ta")
        ]

    def test_intx_splits(self):
        assert token_types(self.lexer.tokenize("intx")) == [
            ("INT", "int"), ("IDENT", "x")
        ]

    def test_cos2x_no_split(self):
        # 'cos' matches, then '2' is a digit -> separate tokens.
        assert token_types(self.lexer.tokenize("cos2x")) == [
            ("FUNC", "cos"), ("NUMBER", "2"), ("IDENT", "x")
        ]

    def test_ex_splits_to_e_x(self):
        assert token_types(self.lexer.tokenize("ex")) == [
            ("CONSTANT", "e"), ("IDENT", "x")
        ]

    def test_pine_splits(self):
        assert token_types(self.lexer.tokenize("pine")) == [
            ("CONSTANT", "pi"), ("IDENT", "n"), ("CONSTANT", "e")
        ]

    def test_sinx_single_letter_ident(self):
        assert token_types(self.lexer.tokenize("sinx")) == [
            ("FUNC", "sin"), ("IDENT", "x")
        ]


class TestDeriv:
    def setup_method(self):
        self.lexer = Lexer()

    def test_d_dx(self):
        tok = self.lexer.tokenize("d/dx")[0]
        assert tok.type == "DERIV"
        assert tok.value == "x"

    def test_d_dtheta(self):
        tok = self.lexer.tokenize("d/dtheta")[0]
        assert tok.type == "DERIV"
        assert tok.value == "theta"

    def test_d_dy(self):
        tok = self.lexer.tokenize("d/dy")[0]
        assert tok.type == "DERIV"
        assert tok.value == "y"

    def test_deriv_not_with_spaces(self):
        """d / dx should NOT be DERIV — it's DIFF + DIVIDE + DIFF + IDENT."""
        tokens = self.lexer.tokenize("d / dx")
        assert token_types(tokens) == [
            ("DIFF", "d"), ("DIVIDE", "/"), ("DIFF", "d"), ("IDENT", "x")
        ]


class TestNumbers:
    def setup_method(self):
        self.lexer = Lexer()

    def test_integer(self):
        assert token_types(self.lexer.tokenize("42")) == [("NUMBER", "42")]

    def test_decimal(self):
        assert token_types(self.lexer.tokenize("2.5")) == [("NUMBER", "2.5")]

    def test_scientific(self):
        assert token_types(self.lexer.tokenize("2e1")) == [("NUMBER", "2e1")]

    def test_2e_is_number_then_const(self):
        assert token_types(self.lexer.tokenize("2e")) == [
            ("NUMBER", "2"), ("CONSTANT", "e")
        ]


class TestUnicodeConstants:
    def setup_method(self):
        self.lexer = Lexer()

    def test_pi(self):
        tokens = self.lexer.tokenize("π")
        assert tokens[0].type == "CONSTANT"
        assert tokens[0].value == "pi"

    def test_infty(self):
        tokens = self.lexer.tokenize("∞")
        assert tokens[0].type == "CONSTANT"
        assert tokens[0].value == "infty"

    def test_sin_pi(self):
        assert token_types(self.lexer.tokenize("sinπ")) == [
            ("FUNC", "sin"), ("CONSTANT", "pi")
        ]


class TestOperatorsAndDelimiters:
    def setup_method(self):
        self.lexer = Lexer()

    def test_operators(self):
        types = token_types(self.lexer.tokenize("+ - * / ^"))
        assert types == [
            ("PLUS", "+"), ("MINUS", "-"), ("TIMES", "*"),
            ("DIVIDE", "/"), ("POWER", "^"),
        ]

    def test_brackets(self):
        types = token_types(self.lexer.tokenize("()[]"))
        assert types == [
            ("LPAREN", "("), ("RPAREN", ")"),
            ("LBRACKET", "["), ("RBRACKET", "]"),
        ]

    def test_comma(self):
        assert token_types(self.lexer.tokenize(",")) == [("COMMA", ",")]


class TestErrors:
    def setup_method(self):
        self.lexer = Lexer()

    def test_unexpected_character(self):
        with pytest.raises(LexerError):
            self.lexer.tokenize("@")
