from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class StopCode(str, Enum):
    CONVERGED_RESIDUAL     = "CONVERGED_RESIDUAL"
    CONVERGED_STEP         = "CONVERGED_STEP"
    MAX_ITERATIONS_REACHED = "MAX_ITERATIONS_REACHED"
    ZERO_DERIVATIVE        = "ZERO_DERIVATIVE"
    NON_FINITE_VALUE       = "NON_FINITE_VALUE"
    DOMAIN_ERROR           = "DOMAIN_ERROR"
    DIVERGENCE_SUSPECTED   = "DIVERGENCE_SUSPECTED"
    INVALID_PARAMETERS     = "INVALID_PARAMETERS"


@dataclass
class IterationRecord:
    n:            int
    x_n:          float
    f_xn:         float
    df_xn:        float
    x_next:       float | None    # None only when derivative is zero / non-finite
    step_size:    float | None    # |x_next - x_n|, None when x_next is None
    residual:     float           # |f(x_n)|
    df_near_zero: bool = False    # |f'(x_n)| below min_df_threshold
    status:       str  = "running"


@dataclass
class NewtonResult:
    steps:     list[IterationRecord]
    root:      float | None
    converged: bool
    stop_code: StopCode
    message:   str
    warnings:  list[str] = field(default_factory=list)

    @property
    def best_x(self) -> float | None:
        if not self.steps:
            return None
        last = self.steps[-1]
        return last.x_next if last.x_next is not None else last.x_n


def newton_iterate(
    f:                   Callable[[float], float],
    df:                  Callable[[float], float],
    x0:                  float,
    tol:                 float = 1e-8,
    max_iter:            int   = 50,
    min_df_threshold:    float = 1e-12,
    divergence_threshold: float = 1e8,
) -> NewtonResult:
    """Run Newton's method and return a complete result with iteration history.

    Parameters
    ----------
    f, df               : callables for f(x) and f'(x)
    x0                  : initial guess (must be finite)
    tol                 : convergence tolerance (must be > 0)
    max_iter            : maximum number of iterations (must be >= 1)
    min_df_threshold    : |f'| below this value sets df_near_zero flag
    divergence_threshold: |x_next| above this triggers DIVERGENCE_SUSPECTED

    Returns
    -------
    NewtonResult with complete step history and diagnostic stop_code.

    Raises
    ------
    ValueError  for invalid parameters (tol <= 0, max_iter < 1, non-finite x0).
    """
    if tol <= 0:
        raise ValueError(f"tol must be positive, got {tol!r}")
    if max_iter < 1:
        raise ValueError(f"max_iter must be >= 1, got {max_iter!r}")
    if not math.isfinite(x0):
        raise ValueError(f"x0 must be finite, got {x0!r}")

    steps:    list[IterationRecord] = []
    warnings: list[str]             = []
    x = float(x0)

    for n in range(max_iter):
        # ---- Evaluate f and f' at current x --------------------------------
        try:
            fx  = float(f(x))
            dfx = float(df(x))
        except (ValueError, ZeroDivisionError, OverflowError,
                FloatingPointError) as exc:
            steps.append(IterationRecord(
                n=n, x_n=x, f_xn=float("nan"), df_xn=float("nan"),
                x_next=None, step_size=None, residual=float("nan"),
                status=StopCode.DOMAIN_ERROR.value,
            ))
            return NewtonResult(
                steps=steps, root=None, converged=False,
                stop_code=StopCode.DOMAIN_ERROR,
                message=f"Domain error at x = {x:.6g}: {exc}",
                warnings=warnings,
            )

        if not math.isfinite(fx) or not math.isfinite(dfx):
            steps.append(IterationRecord(
                n=n, x_n=x, f_xn=fx, df_xn=dfx,
                x_next=None, step_size=None,
                residual=abs(fx) if math.isfinite(fx) else float("nan"),
                status=StopCode.NON_FINITE_VALUE.value,
            ))
            return NewtonResult(
                steps=steps, root=None, converged=False,
                stop_code=StopCode.NON_FINITE_VALUE,
                message=(
                    f"Non-finite value at step {n}: "
                    f"f = {fx}, f′ = {dfx}."
                ),
                warnings=warnings,
            )

        residual     = abs(fx)
        df_near_zero = 0.0 < abs(dfx) < min_df_threshold

        if df_near_zero:
            warnings.append(
                f"Near-zero derivative at step {n}: f′(x) = {dfx:.3e}"
            )

        # ---- Zero derivative — cannot continue ------------------------------
        if dfx == 0.0:
            steps.append(IterationRecord(
                n=n, x_n=x, f_xn=fx, df_xn=dfx,
                x_next=None, step_size=None, residual=residual,
                df_near_zero=False,
                status=StopCode.ZERO_DERIVATIVE.value,
            ))
            return NewtonResult(
                steps=steps, root=None, converged=False,
                stop_code=StopCode.ZERO_DERIVATIVE,
                message=(
                    f"f′(x) = 0 at step {n} (x = {x:.6g}). "
                    "The tangent line is horizontal and cannot cross the x-axis."
                ),
                warnings=warnings,
            )

        # ---- Newton step ----------------------------------------------------
        x_next    = x - fx / dfx
        step_size = abs(x_next - x)
        is_last   = (n == max_iter - 1)

        # Convergence by residual (current x is already close enough)
        if residual <= tol:
            steps.append(IterationRecord(
                n=n, x_n=x, f_xn=fx, df_xn=dfx,
                x_next=x_next, step_size=step_size, residual=residual,
                df_near_zero=df_near_zero,
                status=StopCode.CONVERGED_RESIDUAL.value,
            ))
            return NewtonResult(
                steps=steps, root=x, converged=True,
                stop_code=StopCode.CONVERGED_RESIDUAL,
                message=(
                    f"Converged: |f(x)| = {residual:.3e} ≤ {tol:.3e} "
                    f"after {n + 1} iteration(s)."
                ),
                warnings=warnings,
            )

        # Convergence by step size
        if step_size <= tol:
            steps.append(IterationRecord(
                n=n, x_n=x, f_xn=fx, df_xn=dfx,
                x_next=x_next, step_size=step_size, residual=residual,
                df_near_zero=df_near_zero,
                status=StopCode.CONVERGED_STEP.value,
            ))
            return NewtonResult(
                steps=steps, root=x_next, converged=True,
                stop_code=StopCode.CONVERGED_STEP,
                message=(
                    f"Converged: step size = {step_size:.3e} ≤ {tol:.3e} "
                    f"after {n + 1} iteration(s)."
                ),
                warnings=warnings,
            )

        # Divergence guard
        if (not math.isfinite(x_next)
                or abs(x_next) > divergence_threshold
                or step_size > divergence_threshold):
            x_next_safe = x_next if math.isfinite(x_next) else None
            step_safe   = step_size if math.isfinite(step_size) else None
            steps.append(IterationRecord(
                n=n, x_n=x, f_xn=fx, df_xn=dfx,
                x_next=x_next_safe, step_size=step_safe, residual=residual,
                df_near_zero=df_near_zero,
                status=StopCode.DIVERGENCE_SUSPECTED.value,
            ))
            return NewtonResult(
                steps=steps, root=None, converged=False,
                stop_code=StopCode.DIVERGENCE_SUSPECTED,
                message=(
                    f"Divergence suspected at step {n}: "
                    f"|x_next| = {abs(x_next):.3e}. "
                    "Try a different starting point."
                ),
                warnings=warnings,
            )

        # Max iterations on the last loop turn
        if is_last:
            steps.append(IterationRecord(
                n=n, x_n=x, f_xn=fx, df_xn=dfx,
                x_next=x_next, step_size=step_size, residual=residual,
                df_near_zero=df_near_zero,
                status=StopCode.MAX_ITERATIONS_REACHED.value,
            ))
            return NewtonResult(
                steps=steps, root=None, converged=False,
                stop_code=StopCode.MAX_ITERATIONS_REACHED,
                message=(
                    f"Did not converge in {max_iter} iteration(s). "
                    f"Best approximation: x ≈ {x_next:.6g}, "
                    f"|f(x)| = {residual:.3e}."
                ),
                warnings=warnings,
            )

        # Still running — store record and continue
        steps.append(IterationRecord(
            n=n, x_n=x, f_xn=fx, df_xn=dfx,
            x_next=x_next, step_size=step_size, residual=residual,
            df_near_zero=df_near_zero,
            status="running",
        ))
        x = x_next

    # Should be unreachable (is_last guard above handles it), but satisfies type checkers
    return NewtonResult(
        steps=steps, root=None, converged=False,
        stop_code=StopCode.MAX_ITERATIONS_REACHED,
        message=f"Did not converge in {max_iter} iteration(s).",
        warnings=warnings,
    )


def tangent_line(x_n: float, f_xn: float, df_xn: float) -> tuple[float, float]:
    """Return (slope, y_intercept) of the tangent at x_n.

    Line equation: y = slope * x + intercept
    """
    return df_xn, f_xn - df_xn * x_n
