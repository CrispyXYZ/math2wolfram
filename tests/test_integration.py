import pytest
from math2wolfram import convert
from math2wolfram.errors import ParseError, LexerError


class TestSpecExamples:
    def test_sinx(self):
        assert convert("sinx") == "Sin[x]"

    def test_sin_pi_x(self):
        assert convert("sinπx") == "Sin[Times[Pi, x]]"

    def test_4x_div_3y(self):
        assert convert("4x/3y") == "Times[Times[4, x], Power[Times[3, y], -1]]"

    def test_ddx_sinx_cosx(self):
        assert convert("d/dx sinx cosx") == "D[Times[Sin[x], Cos[x]], x]"

    def test_int_sinx_dx(self):
        assert convert("int sinx d x") == "Integrate[Sin[x], x]"

    def test_int_definite(self):
        assert convert("int [1,2] sinx d x") == "Integrate[Sin[x], {x, 1, 2}]"

    def test_sin_cos_xy(self):
        assert convert("sin cos x y") == "Sin[Cos[Times[x, y]]]"

    def test_sin_2x(self):
        assert convert("sin 2 x") == "Sin[Times[2, x]]"

    def test_sin_paren_pi_times_x(self):
        assert convert("sin(π)x") == "Times[Sin[Pi], x]"

    def test_neg_x(self):
        assert convert("-x") == "Times[-1, x]"

    def test_sin_x_pow_2(self):
        assert convert("sin x ^ 2") == "Power[Sin[x], 2]"

    def test_ddx_sinx_cosx_plus_1(self):
        assert convert("d/dx sinx cosx + 1") == "Plus[D[Times[Sin[x], Cos[x]], x], 1]"


class TestEdgeCases:
    def test_nested_integral(self):
        result = convert("int int x d x d y")
        assert "Integrate" in result

    def test_expr_in_parens(self):
        assert convert("(x+y)") == "Plus[x, y]"

    def test_function_chain(self):
        assert convert("sin cosx") == "Sin[Cos[x]]"

    def test_multiple_trig(self):
        result = convert("sinx + cosx")
        assert "Sin[x]" in result
        assert "Cos[x]" in result


class TestErrors:
    def test_d_as_identifier_fails(self):
        # 'd' alone is DIFF token; if it appears in a spot that expects an
        # expression, the parser should complain.
        with pytest.raises(ParseError):
            convert("x + d")

    def test_int_without_d(self):
        with pytest.raises(ParseError) as exc:
            convert("int sinx x")
        assert "d" in str(exc.value).lower()

    def test_int_d_without_var(self):
        with pytest.raises(ParseError):
            convert("int sinx d")

    def test_func_without_arg(self):
        with pytest.raises(ParseError):
            convert("sin + 1")

    def test_bad_char(self):
        with pytest.raises(LexerError):
            convert("@")
