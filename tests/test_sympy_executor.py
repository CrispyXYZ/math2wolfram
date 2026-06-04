import pytest
from mathio.sympy_executor import SymPyExecutor
from mathio.ast_nodes import (
    BinaryOp, Constant, DefiniteIntegral, Derivative, FuncCall,
    Identifier, ImplicitMultiply, Integral, Negation, Number,
)


executor = SymPyExecutor()


def ev(node, fmt="plain"):
    return executor.evaluate(node, fmt=fmt)


class TestNumbers:
    def test_integer(self):
        assert ev(Number("42")) == "42"

    def test_decimal_is_exact(self):
        result = executor.execute(Number("0.1"))
        import sympy
        assert isinstance(result, sympy.Rational)
        assert result == sympy.Rational(1, 10)

    def test_scientific_notation(self):
        result = executor.execute(Number("1e-10"))
        import sympy
        assert result == sympy.Rational(1, 10**10)

    def test_scientific_with_decimal(self):
        result = executor.execute(Number("1.5e3"))
        import sympy
        assert result == sympy.Integer(1500)


class TestConstants:
    def test_pi(self):
        import sympy
        assert executor.execute(Constant("pi")) == sympy.pi

    def test_e(self):
        import sympy
        assert executor.execute(Constant("e")) == sympy.E

    def test_infty(self):
        import sympy
        assert executor.execute(Constant("infty")) == sympy.oo


class TestIdentifiers:
    def test_single_symbol(self):
        import sympy
        result = executor.execute(Identifier("x"))
        assert isinstance(result, sympy.Symbol)
        assert str(result) == "x"


class TestBinaryOps:
    def test_addition(self):
        assert ev(BinaryOp("+", Number("2"), Number("3"))) == "5"

    def test_subtraction(self):
        assert ev(BinaryOp("-", Number("5"), Number("3"))) == "2"

    def test_multiplication(self):
        assert ev(BinaryOp("*", Number("2"), Identifier("x"))) == "2*x"

    def test_division(self):
        result = executor.execute(BinaryOp("/", Number("1"), Number("3")))
        import sympy
        assert result == sympy.Rational(1, 3)

    def test_power(self):
        assert ev(BinaryOp("^", Identifier("x"), Number("2"))) == "x**2"


class TestImplicitMultiply:
    def test_two_vars(self):
        assert ev(ImplicitMultiply([Identifier("x"), Identifier("y")])) == "x*y"

    def test_same_var_merges(self):
        result = executor.execute(ImplicitMultiply([Identifier("x"), Identifier("x")]))
        import sympy
        assert result == sympy.Pow(sympy.Symbol("x"), sympy.Integer(2))


class TestFuncCall:
    def test_sin(self):
        result = executor.execute(FuncCall("sin", Constant("pi")))
        import sympy
        assert result == 0

    def test_cos(self):
        result = executor.execute(FuncCall("cos", Constant("pi")))
        import sympy
        assert result == -1

    def test_ln_is_log(self):
        result = executor.execute(FuncCall("ln", Identifier("x")))
        import sympy
        assert result == sympy.log(sympy.Symbol("x"))


class TestIntegral:
    def test_indefinite_sinx(self):
        import sympy
        result = executor.execute(
            Integral("x", FuncCall("sin", Identifier("x")))
        )
        assert result == -sympy.cos(sympy.Symbol("x"))

    def test_definite_x_0_to_1(self):
        result = executor.execute(
            DefiniteIntegral("x", Identifier("x"), Number("0"), Number("1"))
        )
        import sympy
        assert result == sympy.Rational(1, 2)


class TestDerivative:
    def test_ddx_sinx(self):
        import sympy
        result = executor.execute(
            Derivative("x", FuncCall("sin", Identifier("x")))
        )
        assert result == sympy.cos(sympy.Symbol("x"))

    def test_ddx_x_squared(self):
        result = executor.execute(
            Derivative("x", BinaryOp("^", Identifier("x"), Number("2")))
        )
        assert ev(Derivative("x", BinaryOp("^", Identifier("x"), Number("2")))) == "2*x"


class TestNegation:
    def test_neg_number(self):
        assert ev(Negation(Number("5"))) == "-5"

    def test_neg_var(self):
        assert ev(Negation(Identifier("x"))) == "-x"


class TestPrettyOutput:
    def test_pretty_uses_unicode(self):
        result = ev(BinaryOp("/", Identifier("x"), Number("2")), fmt="pretty")
        assert "─" in result or "x" in result
