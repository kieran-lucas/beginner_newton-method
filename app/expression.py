"""Safe expression parsing and symbolic differentiation using SymPy.

Users may enter expressions with:
  - Python notation:   x**2 - 2,  cos(x) - x
  - Caret exponents:   x^2 - 2,   (x-1)^3
  - Implicit multiply: 2x,        3sin(x)
  - Common functions:  sin, cos, tan, exp, log, ln, sqrt, abs
  - Constants:         pi, e

The derivative is computed symbolically, then both f and f' are compiled
to numeric callables via lambdify (numpy/math modules).
"""
from __future__ import annotations

import math
import warnings as _warnings
from typing import Callable

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

_x = sp.Symbol("x")

_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

_SAFE_LOCALS: dict[str, object] = {
    "x":    _x,
    "sin":  sp.sin,
    "cos":  sp.cos,
    "tan":  sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "exp":  sp.exp,
    "log":  sp.log,
    "ln":   sp.log,   # common alias
    "sqrt": sp.sqrt,
    "abs":  sp.Abs,
    "Abs":  sp.Abs,
    "pi":   sp.pi,
    "e":    sp.E,
    "E":    sp.E,
}


def _prettify(s: str) -> str:
    """Make a SymPy str() output slightly more readable for display."""
    s = s.replace("**", "^")
    s = s.replace("*", "·")   # middle dot
    return s


def parse_expression(
    expr_str: str,
) -> tuple[
    Callable[[float], float],   # f(x)
    Callable[[float], float],   # f'(x)
    str,                        # human-readable f(x)
    str,                        # human-readable f'(x)
]:
    """Parse a user-entered expression string.

    Returns
    -------
    (f, df, f_str, df_str)
        f, df   : numeric callables that raise ValueError on domain errors
        f_str   : display string for f(x)  (e.g. "x^2 - 2")
        df_str  : display string for f'(x) (e.g. "2·x")

    Raises
    ------
    ValueError  for empty input, parse errors, unknown variables, or
                expressions that evaluate to complex numbers.
    """
    if not expr_str or not expr_str.strip():
        raise ValueError("Expression is empty.")

    # --- Parse with SymPy ---------------------------------------------------
    try:
        expr = parse_expr(
            expr_str.strip(),
            local_dict=_SAFE_LOCALS,
            transformations=_TRANSFORMATIONS,
            evaluate=True,
        )
    except Exception as exc:
        raise ValueError(f"Could not parse ‘{expr_str}’: {exc}") from exc

    # Reject unknown symbols (anything that isn’t x)
    unknown = expr.free_symbols - {_x}
    if unknown:
        names = ", ".join(str(s) for s in sorted(unknown, key=str))
        raise ValueError(
            f"Unknown variable(s): {names}. Use ‘x’ as the only variable."
        )

    # Reject constant expressions (no x present)
    if _x not in expr.free_symbols:
        raise ValueError(
            "Expression has no variable ‘x’. Enter a function of x, e.g. x**2 - 2."
        )

    # --- Symbolic derivative ------------------------------------------------
    try:
        deriv_expr = sp.diff(expr, _x)
    except Exception as exc:
        raise ValueError(f"Could not differentiate ‘{expr_str}’: {exc}") from exc

    # --- Compile to numeric callables ---------------------------------------
    import numpy as np

    _modules = [
        {"zoo": float("nan"), "oo": float("inf"), "nan": float("nan")},
        "numpy",
        "math",
    ]

    try:
        _f_raw  = sp.lambdify(_x, expr,       modules=_modules)
        _df_raw = sp.lambdify(_x, deriv_expr, modules=_modules)
    except Exception as exc:
        raise ValueError(f"Could not compile expression: {exc}") from exc

    # --- Wrappers with domain-error handling --------------------------------

    def _eval(raw_fn: Callable, x_val: float, label: str) -> float:
        with _warnings.catch_warnings():
            _warnings.simplefilter("error")
            try:
                result = raw_fn(float(x_val))
                # lambdify with numpy may return a 0-d array
                val = float(np.asarray(result).flat[0])
            except (TypeError, ValueError, ZeroDivisionError,
                    OverflowError, FloatingPointError,
                    Warning) as exc:
                raise ValueError(
                    f"Cannot evaluate {label}({x_val:.6g}): {exc}"
                ) from exc

        if not math.isfinite(val):
            raise ValueError(f"{label}({x_val:.6g}) = {val} (not finite)")
        return val

    def f(x_val: float) -> float:
        return _eval(_f_raw, x_val, "f")

    def df(x_val: float) -> float:
        return _eval(_df_raw, x_val, "f′")

    f_str  = _prettify(str(expr))
    df_str = _prettify(str(deriv_expr))

    return f, df, f_str, df_str
