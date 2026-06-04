import pytest
from mathio import convert, to_wolfram
from mathio.errors import ParseError, LexerError


class TestSymPyDefault:
    """convert() now evaluates with SymPy by default."""

    def test_sinx(self):
        assert convert("sinx") == "sin(x)"

    def test_sin_pi_x(self):
        assert convert("sinπx", fmt="plain") == "sin(pi*x)"

    def test_sin_2x(self):
        assert convert("sin 2 x", fmt="plain") == "sin(2*x)"

    def test_neg_x(self):
        assert convert("-x", fmt="plain") == "-x"

    def test_explicit_mul(self):
        # sin(pi) is 0, so sin(π)x simplifies to 0.
        assert convert("sin(π)x", fmt="plain") == "0"

    def test_arith(self):
        assert convert("2+3", fmt="plain") == "5"

    def test_latex(self):
        result = convert("sin(π/4)", fmt="latex")
        assert r"\frac" in result and r"\sqrt{2}" in result


class TestWolframMode:
    """to_wolfram() generates Wolfram Language code."""

    def test_sinx(self):
        assert to_wolfram("sinx") == "Sin[x]"

    def test_sin_pi_x(self):
        assert to_wolfram("sinπx") == "Sin[Times[Pi, x]]"

    def test_4x_div_3y(self):
        assert to_wolfram("4x/3y") == "Times[Times[4, x], Power[Times[3, y], -1]]"

    def test_ddx_sinx_cosx(self):
        assert to_wolfram("d/dx sinx cosx") == "D[Times[Sin[x], Cos[x]], x]"

    def test_int_sinx_dx(self):
        assert to_wolfram("int sinx d x") == "Integrate[Sin[x], x]"

    def test_int_definite(self):
        assert to_wolfram("int [1,2] sinx d x") == "Integrate[Sin[x], {x, 1, 2}]"

    def test_sin_cos_xy(self):
        assert to_wolfram("sin cos x y") == "Sin[Cos[Times[x, y]]]"

    def test_sin_2x(self):
        assert to_wolfram("sin 2 x") == "Sin[Times[2, x]]"

    def test_sin_paren_pi_times_x(self):
        assert to_wolfram("sin(π)x") == "Times[Sin[Pi], x]"

    def test_neg_x(self):
        assert to_wolfram("-x") == "Times[-1, x]"

    def test_sin_x_pow_2(self):
        assert to_wolfram("sin x ^ 2") == "Power[Sin[x], 2]"

    def test_ddx_sinx_cosx_plus_1(self):
        assert to_wolfram("d/dx sinx cosx + 1") == "Plus[D[Times[Sin[x], Cos[x]], x], 1]"


class TestEdgeCases:
    def test_expr_in_parens_sympy(self):
        assert convert("(x+y)", fmt="plain") == "x + y"

    def test_expr_in_parens_wolfram(self):
        assert to_wolfram("(x+y)") == "Plus[x, y]"

    def test_function_chain_sympy(self):
        assert convert("sin cosx", fmt="plain") == "sin(cos(x))"

    def test_function_chain_wolfram(self):
        assert to_wolfram("sin cosx") == "Sin[Cos[x]]"

    def test_multiple_trig_sympy(self):
        result = convert("sinx + cosx", fmt="plain")
        assert "sin(x)" in result
        assert "cos(x)" in result

    def test_multiple_trig_wolfram(self):
        result = to_wolfram("sinx + cosx")
        assert "Sin[x]" in result
        assert "Cos[x]" in result


class TestErrors:
    def test_d_as_identifier_fails(self):
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
