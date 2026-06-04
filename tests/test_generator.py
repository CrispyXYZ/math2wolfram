from mathio.wolfram_generator import WolframGenerator
from mathio.ast_nodes import (
    BinaryOp, Constant, DefiniteIntegral, Derivative, FuncCall,
    Identifier, ImplicitMultiply, Integral, Negation, Number,
)


def gen(node):
    return WolframGenerator().generate(node)


class TestAtoms:
    def test_number(self):
        assert gen(Number("42")) == "42"

    def test_constant_pi(self):
        assert gen(Constant("pi")) == "Pi"

    def test_constant_e(self):
        assert gen(Constant("e")) == "E"

    def test_constant_infty(self):
        assert gen(Constant("infty")) == "Infinity"

    def test_identifier(self):
        assert gen(Identifier("x")) == "x"


class TestBinaryOps:
    def test_plus(self):
        assert gen(BinaryOp("+", Identifier("x"), Identifier("y"))) == "Plus[x, y]"

    def test_minus(self):
        assert gen(BinaryOp("-", Identifier("x"), Identifier("y"))) == "Subtract[x, y]"

    def test_times(self):
        assert gen(BinaryOp("*", Identifier("x"), Identifier("y"))) == "Times[x, y]"

    def test_divide(self):
        assert gen(BinaryOp("/", Number("4"), Identifier("y"))) == "Times[4, Power[y, -1]]"

    def test_power(self):
        assert gen(BinaryOp("^", Identifier("x"), Number("2"))) == "Power[x, 2]"


class TestImplicitMultiply:
    def test_two(self):
        assert gen(ImplicitMultiply([Identifier("x"), Identifier("y")])) == "Times[x, y]"

    def test_three(self):
        assert gen(ImplicitMultiply([Identifier("x"), Identifier("y"), Identifier("z")])
                   ) == "Times[x, y, z]"


class TestFuncCall:
    def test_sin(self):
        assert gen(FuncCall("sin", Identifier("x"))) == "Sin[x]"

    def test_cos(self):
        assert gen(FuncCall("cos", Identifier("x"))) == "Cos[x]"

    def test_log(self):
        assert gen(FuncCall("log", Identifier("x"))) == "Log[x]"


class TestCalculus:
    def test_indefinite_integral(self):
        assert gen(Integral("x", FuncCall("sin", Identifier("x")))) == "Integrate[Sin[x], x]"

    def test_definite_integral(self):
        assert gen(DefiniteIntegral("x", FuncCall("sin", Identifier("x")),
                                    Number("1"), Number("2"))
                   ) == "Integrate[Sin[x], {x, 1, 2}]"

    def test_derivative(self):
        assert gen(Derivative("x", FuncCall("sin", Identifier("x")))) == "D[Sin[x], x]"


class TestNegation:
    def test_neg_x(self):
        assert gen(Negation(Identifier("x"))) == "Times[-1, x]"

    def test_neg_number(self):
        assert gen(Negation(Number("5"))) == "Times[-1, 5]"
