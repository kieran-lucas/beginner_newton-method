"""Tests for the Newton numerical core (app/newton.py).

Numerical assertions use tolerances rather than exact equality.
"""
import math
import pytest

from app.newton import (
    IterationRecord, NewtonResult, StopCode,
    newton_iterate, tangent_line,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def f_quadratic(x):  return x**2 - 2
def df_quadratic(x): return 2*x

def f_cubic(x):  return x**3 - x - 2
def df_cubic(x): return 3*x**2 - 1

def f_trig(x):  return math.cos(x) - x
def df_trig(x): return -math.sin(x) - 1

def f_zero_at_one(x):  return x - 1.0      # root at 1.0
def df_zero_at_one(x): return 1.0

def f_deriv_zero(x):  return x**2           # derivative 0 at x=0
def df_deriv_zero(x): return 2*x

def f_domain_error(x): return math.log(x)  # undefined for x <= 0
def df_domain_error(x): return 1.0 / x

# ---------------------------------------------------------------------------
# Convergence — simple polynomial
# ---------------------------------------------------------------------------

def test_quadratic_converges():
    result = newton_iterate(f_quadratic, df_quadratic, x0=1.0)
    assert result.converged
    assert result.root is not None
    assert abs(result.root - math.sqrt(2)) < 1e-7
    assert result.stop_code in (
        StopCode.CONVERGED_RESIDUAL, StopCode.CONVERGED_STEP
    )


def test_quadratic_from_negative_side():
    result = newton_iterate(f_quadratic, df_quadratic, x0=-1.0)
    assert result.converged
    assert result.root is not None
    assert abs(result.root - (-math.sqrt(2))) < 1e-7


def test_cubic_converges():
    result = newton_iterate(f_cubic, df_cubic, x0=2.0)
    assert result.converged
    assert result.root is not None
    # Known root ≈ 1.5213797...
    assert abs(result.root - 1.5213797) < 1e-5


def test_trig_converges():
    result = newton_iterate(f_trig, df_trig, x0=1.0)
    assert result.converged
    assert result.root is not None
    assert abs(result.root - 0.739085133) < 1e-7


# ---------------------------------------------------------------------------
# Iteration records are complete and correct
# ---------------------------------------------------------------------------

def test_iteration_fields_populated():
    result = newton_iterate(f_quadratic, df_quadratic, x0=1.0)
    assert len(result.steps) > 0
    for s in result.steps:
        assert isinstance(s, IterationRecord)
        assert math.isfinite(s.x_n)
        assert math.isfinite(s.f_xn)
        assert math.isfinite(s.df_xn)
        assert math.isfinite(s.residual)
        assert s.residual == abs(s.f_xn)


def test_step_zero_is_initial_guess():
    result = newton_iterate(f_quadratic, df_quadratic, x0=2.0)
    assert result.steps[0].x_n == 2.0


def test_x_next_matches_formula():
    result = newton_iterate(f_quadratic, df_quadratic, x0=2.0)
    s = result.steps[0]
    expected_x_next = s.x_n - s.f_xn / s.df_xn
    assert abs(s.x_next - expected_x_next) < 1e-12


def test_step_size_matches_diff():
    result = newton_iterate(f_quadratic, df_quadratic, x0=2.0)
    for s in result.steps:
        if s.x_next is not None and s.step_size is not None:
            assert abs(s.step_size - abs(s.x_next - s.x_n)) < 1e-12


# ---------------------------------------------------------------------------
# Failure cases
# ---------------------------------------------------------------------------

def test_zero_derivative_stops_immediately():
    # f'(0) = 0 for f(x) = x^2
    result = newton_iterate(f_deriv_zero, df_deriv_zero, x0=0.0)
    assert not result.converged
    assert result.stop_code == StopCode.ZERO_DERIVATIVE
    assert len(result.steps) == 1
    assert result.steps[0].x_next is None


def test_domain_error_handled():
    result = newton_iterate(f_domain_error, df_domain_error, x0=-1.0)
    assert not result.converged
    assert result.stop_code == StopCode.DOMAIN_ERROR
    assert len(result.steps) == 1


def test_max_iterations_stop():
    result = newton_iterate(f_trig, df_trig, x0=1.0, max_iter=2)
    assert not result.converged
    assert result.stop_code == StopCode.MAX_ITERATIONS_REACHED
    assert len(result.steps) == 2


def test_divergence_detected():
    # Near-zero derivative causes x_next to fly off to -1e10.
    # With divergence_threshold=100, this triggers DIVERGENCE_SUSPECTED.
    eps = 1e-10
    result = newton_iterate(
        lambda x: x,
        lambda x: eps,
        x0=1.0,
        divergence_threshold=100.0,
    )
    assert result.stop_code == StopCode.DIVERGENCE_SUSPECTED


# ---------------------------------------------------------------------------
# Invalid parameters → ValueError
# ---------------------------------------------------------------------------

def test_invalid_tol_zero():
    with pytest.raises(ValueError, match="tol"):
        newton_iterate(f_quadratic, df_quadratic, x0=1.0, tol=0.0)


def test_invalid_tol_negative():
    with pytest.raises(ValueError, match="tol"):
        newton_iterate(f_quadratic, df_quadratic, x0=1.0, tol=-1e-5)


def test_invalid_max_iter_zero():
    with pytest.raises(ValueError, match="max_iter"):
        newton_iterate(f_quadratic, df_quadratic, x0=1.0, max_iter=0)


def test_invalid_x0_infinite():
    with pytest.raises(ValueError, match="x0"):
        newton_iterate(f_quadratic, df_quadratic, x0=float("inf"))


def test_invalid_x0_nan():
    with pytest.raises(ValueError, match="x0"):
        newton_iterate(f_quadratic, df_quadratic, x0=float("nan"))


# ---------------------------------------------------------------------------
# Multi-step convergence visible in iteration history
# ---------------------------------------------------------------------------

def test_multiple_visible_steps():
    # Loose tolerance so we see several steps
    result = newton_iterate(f_quadratic, df_quadratic, x0=10.0, tol=1e-4)
    assert result.converged
    assert len(result.steps) > 2, "Expected multiple visible steps from x0=10"
    # Steps should be getting closer to root
    residuals = [s.residual for s in result.steps]
    assert residuals[-1] < residuals[0]


def test_already_at_root():
    result = newton_iterate(f_zero_at_one, df_zero_at_one, x0=1.0)
    assert result.converged
    assert len(result.steps) == 1
    assert result.steps[0].residual == 0.0


# ---------------------------------------------------------------------------
# tangent_line utility
# ---------------------------------------------------------------------------

def test_tangent_line_slope_intercept():
    slope, intercept = tangent_line(x_n=2.0, f_xn=2.0, df_xn=4.0)
    assert slope == 4.0
    # intercept = f_xn - df_xn * x_n = 2 - 4*2 = -6
    assert intercept == -6.0


def test_tangent_line_x_intercept():
    slope, intercept = tangent_line(x_n=2.0, f_xn=2.0, df_xn=4.0)
    # x-intercept: 0 = slope*x + intercept → x = -intercept/slope
    x_cross = -intercept / slope
    # Should equal x_n - f_xn/df_xn = 2 - 2/4 = 1.5
    assert abs(x_cross - 1.5) < 1e-12


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------

def test_near_zero_derivative_warning():
    # Construct a function where the derivative is tiny
    def f_flat(x): return (x - 1) * 1e-14
    def df_flat(x): return 1e-14

    result = newton_iterate(f_flat, df_flat, x0=0.0, min_df_threshold=1e-10)
    assert len(result.warnings) > 0
    assert any("near-zero" in w.lower() for w in result.warnings)
