"""Tests for safe expression parsing (app/expression.py)."""
import math
import pytest

from app.expression import parse_expression


# ---------------------------------------------------------------------------
# Valid expressions
# ---------------------------------------------------------------------------

def test_quadratic_f_value():
    f, df, f_str, df_str = parse_expression("x**2 - 2")
    assert abs(f(2.0) - 2.0)  < 1e-12
    assert abs(f(0.0) + 2.0)  < 1e-12


def test_quadratic_df_value():
    _, df, _, _ = parse_expression("x**2 - 2")
    assert abs(df(1.0) - 2.0)  < 1e-10
    assert abs(df(3.0) - 6.0)  < 1e-10


def test_caret_notation():
    f1, _, _, _ = parse_expression("x**2 - 2")
    f2, _, _, _ = parse_expression("x^2 - 2")
    assert abs(f1(3.0) - f2(3.0)) < 1e-12


def test_trig_cos():
    f, df, _, _ = parse_expression("cos(x) - x")
    assert abs(f(0.0) - 1.0) < 1e-12
    # f'(x) = -sin(x) - 1; at 0: -sin(0) - 1 = -1
    assert abs(df(0.0) + 1.0) < 1e-10


def test_trig_sin():
    f, _, _, _ = parse_expression("sin(x)")
    assert abs(f(0.0)           ) < 1e-12
    assert abs(f(math.pi / 2) - 1.0) < 1e-10


def test_exp_expression():
    f, df, _, _ = parse_expression("exp(x) - 2")
    # f(0) = 1 - 2 = -1
    assert abs(f(0.0) + 1.0) < 1e-12
    # f'(x) = exp(x); f'(0) = 1
    assert abs(df(0.0) - 1.0) < 1e-10


def test_log_expression():
    f, _, _, _ = parse_expression("log(x) - 1")
    assert abs(f(math.e)) < 1e-10


def test_ln_alias():
    f1, _, _, _ = parse_expression("log(x)")
    f2, _, _, _ = parse_expression("ln(x)")
    assert abs(f1(math.e) - f2(math.e)) < 1e-12


def test_sqrt_expression():
    f, df, _, _ = parse_expression("sqrt(x) - 2")
    assert abs(f(4.0)) < 1e-12
    # f'(x) = 1/(2*sqrt(x)); f'(4) = 0.25
    assert abs(df(4.0) - 0.25) < 1e-10


def test_implicit_multiplication():
    f, _, _, _ = parse_expression("2*x - 4")
    assert abs(f(2.0)) < 1e-12


def test_display_strings_returned():
    _, _, f_str, df_str = parse_expression("x**2 - 2")
    assert f_str
    assert df_str
    assert "x" in f_str.lower() or "2" in f_str


# ---------------------------------------------------------------------------
# Invalid syntax
# ---------------------------------------------------------------------------

def test_empty_expression():
    with pytest.raises(ValueError, match="[Ee]mpty"):
        parse_expression("")


def test_whitespace_only():
    with pytest.raises(ValueError, match="[Ee]mpty"):
        parse_expression("   ")


def test_invalid_syntax():
    with pytest.raises(ValueError):
        parse_expression("x + + +")


def test_unknown_variable():
    with pytest.raises(ValueError, match="[Uu]nknown"):
        parse_expression("y**2 - 1")


# ---------------------------------------------------------------------------
# Domain errors from callables
# ---------------------------------------------------------------------------

def test_log_domain_negative():
    _, _, _, _ = parse_expression("log(x) - 1")   # parse should succeed
    f, _, _, _ = parse_expression("log(x) - 1")
    with pytest.raises(ValueError):
        f(-1.0)


def test_log_domain_zero():
    f, _, _, _ = parse_expression("log(x)")
    with pytest.raises(ValueError):
        f(0.0)


def test_sqrt_negative():
    f, _, _, _ = parse_expression("sqrt(x)")
    with pytest.raises(ValueError):
        f(-1.0)


# ---------------------------------------------------------------------------
# Derivative correctness
# ---------------------------------------------------------------------------

def test_derivative_cubic():
    _, df, _, _ = parse_expression("x**3 - x - 2")
    # f'(x) = 3x^2 - 1; at x=2: 11
    assert abs(df(2.0) - 11.0) < 1e-9


def test_derivative_trig():
    _, df, _, _ = parse_expression("sin(x)")
    # f'(x) = cos(x); f'(0) = 1
    assert abs(df(0.0) - 1.0) < 1e-10
    assert abs(df(math.pi) + 1.0) < 1e-10
