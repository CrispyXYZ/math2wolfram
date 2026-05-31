import pytest
from math2wolfram.tokenizer import Lexer
from math2wolfram.parser import Parser
from math2wolfram.ast_nodes import (
    BinaryOp, Constant, DefiniteIntegral, Derivative, FuncCall,
    Identifier, ImplicitMultiply, Integral, Negation, Number,
)
from math2wolfram.errors import ParseError


def parse(s):
    lexer = Lexer()
    parser = Parser()
    return parser.parse(lexer.tokenize(s), s)


class TestAtoms:
    def test_number(self):
        assert parse("42") == Number(value="42")

    def test_decimal(self):
        assert parse("2.5") == Number(value="2.5")

    def test_constant(self):
        assert parse("pi") == Constant(name="pi")

    def test_identifier(self):
        assert parse("x") == Identifier(name="x")

    def test_parenthesized(self):
        assert parse("(x)") == Identifier(name="x")


class TestBinaryOps:
    def test_addition(self):
        assert parse("x+y") == BinaryOp("+", Identifier("x"), Identifier("y"))

    def test_subtraction(self):
        assert parse("x-y") == BinaryOp("-", Identifier("x"), Identifier("y"))

    def test_multiplication(self):
        assert parse("x*y") == BinaryOp("*", Identifier("x"), Identifier("y"))

    def test_division(self):
        assert parse("x/y") == BinaryOp("/", Identifier("x"), Identifier("y"))

    def test_power(self):
        assert parse("x^y") == BinaryOp("^", Identifier("x"), Identifier("y"))

    def test_power_right_assoc(self):
        ast = parse("x^y^z")
        assert ast == BinaryOp("^", Identifier("x"),
                               BinaryOp("^", Identifier("y"), Identifier("z")))


class TestImplicitMultiply:
    def test_two_vars(self):
        assert parse("x y") == ImplicitMultiply([Identifier("x"), Identifier("y")])

    def test_three_vars(self):
        assert parse("x y z") == ImplicitMultiply([
            Identifier("x"), Identifier("y"), Identifier("z"),
        ])

    def test_number_and_var(self):
        assert parse("2 x") == ImplicitMultiply([Number("2"), Identifier("x")])

    def test_single_factor_no_wrap(self):
        assert parse("x") == Identifier("x")


class TestFuncApp:
    def test_sinx(self):
        assert parse("sinx") == FuncCall("sin", Identifier("x"))

    def test_sin_paren(self):
        assert parse("sin(x)") == FuncCall("sin", Identifier("x"))

    def test_sin_2x(self):
        assert parse("sin 2 x") == FuncCall(
            "sin", ImplicitMultiply([Number("2"), Identifier("x")])
        )

    def test_sin_cos_xy(self):
        ast = parse("sin cos x y")
        assert ast == FuncCall(
            "sin",
            FuncCall("cos", ImplicitMultiply([Identifier("x"), Identifier("y")])),
        )

    def test_sinx_cosx(self):
        ast = parse("sin x cos x")
        assert ast == ImplicitMultiply([
            FuncCall("sin", Identifier("x")),
            FuncCall("cos", Identifier("x")),
        ])

    def test_func_without_arg(self):
        with pytest.raises(ParseError):
            parse("sin + 1")


class TestDerivative:
    def test_ddx_sinx(self):
        ast = parse("d/dx sinx")
        assert ast == Derivative("x", FuncCall("sin", Identifier("x")))

    def test_ddx_sinx_cosx(self):
        ast = parse("d/dx sinx cosx")
        assert ast == Derivative("x", ImplicitMultiply([
            FuncCall("sin", Identifier("x")),
            FuncCall("cos", Identifier("x")),
        ]))


class TestIntegral:
    def test_indefinite(self):
        ast = parse("int sinx d x")
        assert ast == Integral("x", FuncCall("sin", Identifier("x")))

    def test_definite(self):
        ast = parse("int [1,2] sinx d x")
        assert ast == DefiniteIntegral(
            "x", FuncCall("sin", Identifier("x")),
            Number("1"), Number("2"),
        )

    def test_int_without_d(self):
        with pytest.raises(ParseError):
            parse("int sinx x")

    def test_int_d_without_var(self):
        with pytest.raises(ParseError):
            parse("int sinx d")


class TestUnaryMinus:
    def test_neg_x(self):
        assert parse("-x") == Negation(Identifier("x"))

    def test_neg_number(self):
        assert parse("-5") == Negation(Number("5"))

    def test_double_neg(self):
        assert parse("--x") == Negation(Negation(Identifier("x")))


class TestPrecedence:
    def test_add_mul(self):
        ast = parse("x + y * z")
        assert ast == BinaryOp("+", Identifier("x"),
                               BinaryOp("*", Identifier("y"), Identifier("z")))

    def test_power_prec(self):
        ast = parse("x * y ^ 2")
        assert ast == BinaryOp(
            "*", Identifier("x"),
            BinaryOp("^", Identifier("y"), Number("2")),
        )

    def test_deriv_prec(self):
        ast = parse("d/dx sinx + 1")
        assert ast == BinaryOp(
            "+", Derivative("x", FuncCall("sin", Identifier("x"))),
            Number("1"),
        )
