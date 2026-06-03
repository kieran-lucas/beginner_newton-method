"""Generate plain-English HTML explanations for each iteration step.

All functions return Qt-compatible HTML (QLabel rich text subset).
No UI imports — this module is pure logic.
"""
from __future__ import annotations

from app.newton import IterationRecord, NewtonResult, StopCode
from app import style


def _fmt(val: float, sig: int = 6) -> str:
    """Format a float to sig significant figures, using sci-notation if tiny."""
    if val != val:                   # NaN
        return "NaN"
    if abs(val) < 1e-4 and val != 0:
        return f"{val:.3e}"
    return f"{val:.{sig}g}"


def _sign_sentence(f_xn: float) -> str:
    if abs(f_xn) < 1e-6:
        return "The function value is effectively zero here."
    if f_xn > 0:
        return "The function is positive here — the curve is above the x-axis."
    return "The function is negative here — the curve is below the x-axis."


def build_idle_html() -> str:
    return (
        "<p>Enter a function and an initial guess above, "
        "then press <b>Run</b> to begin.</p>"
        f"<p style='color:{style.COLOR_TEXT_SECONDARY};'>"
        "Newton's method finds a root of f(x) by drawing the tangent "
        "line at the current approximation and following it to the x-axis."
        "</p>"
    )


def build_step_html(
    step: IterationRecord,
    idx: int,
    total: int,
    result: NewtonResult,
) -> str:
    """Build explanation HTML for the given step."""
    sc = step.status

    header = (
        f"<p style='color:{style.COLOR_TEXT_SECONDARY}; "
        f"font-family:{style.FONT_UI},sans-serif; "
        f"font-size:{style.SIZE_SMALL}pt; font-weight:700; "
        f"letter-spacing:1px; margin-bottom:6px;'>STEP {idx} OF {total - 1}</p>"
    )

    # ---- Failure states ------------------------------------------------
    if sc == StopCode.ZERO_DERIVATIVE.value:
        return header + (
            f"<p>At x = {_fmt(step.x_n)}, the derivative "
            f"f′(x) = {_fmt(step.df_xn)} is exactly <b>zero</b>.</p>"
            "<p>The tangent line is horizontal — it runs parallel to the "
            "x-axis and never crosses it.</p>"
            "<p>Newton's method cannot continue from this point. "
            "Try a different starting guess.</p>"
            f"<p style='color:{style.COLOR_TEXT_SECONDARY};'>"
            "<i>Look at the graph: the tangent is flat, "
            "so there is no x-intercept to move to.</i></p>"
        )

    if sc == StopCode.DOMAIN_ERROR.value:
        return header + (
            f"<p>The function cannot be evaluated at x = {_fmt(step.x_n)}.</p>"
            f"<p style='color:{style.COLOR_ERROR_FG};'>{result.message}</p>"
            "<p>Check that the function is defined for your chosen "
            "starting point (e.g. ln(x) requires x &gt; 0).</p>"
        )

    if sc == StopCode.NON_FINITE_VALUE.value:
        return header + (
            f"<p>At x = {_fmt(step.x_n)}, the function or its derivative "
            "produced a non-finite value (infinity or NaN).</p>"
            "<p>This usually means the function blows up near this point. "
            "Try a starting guess further from singularities or "
            "steep regions.</p>"
        )

    if sc == StopCode.DIVERGENCE_SUSPECTED.value:
        x_next_str = _fmt(step.x_next) if step.x_next is not None else "unknown"
        return header + (
            f"<p>At x = {_fmt(step.x_n)}, the next approximation "
            f"jumped to x = {x_next_str} — far beyond the visible range.</p>"
            "<p>This indicates the method is <b>diverging</b>. The tangent "
            "line at this point, when followed to the x-axis, lands very "
            "far away rather than closer to a root.</p>"
            "<p>Common causes: starting near a local extremum, a function "
            "with very small slope, or a starting point in the wrong region.</p>"
            f"<p style='color:{style.COLOR_TEXT_SECONDARY};'>"
            "<i>Try a different initial guess, or use a preset that "
            "demonstrates convergence first.</i></p>"
        )

    # ---- Converged states -----------------------------------------------
    if sc == StopCode.CONVERGED_RESIDUAL.value:
        return header + _normal_body(step, idx) + (
            f"<p style='color:{style.COLOR_SUCCESS_FG};'>"
            f"<b>|f(x)| = {_fmt(step.residual)} is within the tolerance.</b> "
            "Newton's method stops here.</p>"
        )

    if sc == StopCode.CONVERGED_STEP.value:
        return header + _normal_body(step, idx) + (
            f"<p style='color:{style.COLOR_SUCCESS_FG};'>"
            f"<b>Step size = {_fmt(step.step_size)} is within the tolerance.</b> "
            "The approximation has stabilised — Newton's method stops here.</p>"
        )

    if sc == StopCode.MAX_ITERATIONS_REACHED.value:
        return header + _normal_body(step, idx) + (
            f"<p style='color:{style.COLOR_WARN_FG};'>"
            f"<b>Maximum iterations reached.</b> "
            f"Residual |f(x)| = {_fmt(step.residual)}. "
            "Try increasing max iterations or choosing a closer starting point.</p>"
        )

    # ---- Normal running step --------------------------------------------
    return header + _normal_body(step, idx)


def _normal_body(step: IterationRecord, idx: int) -> str:
    sec_color = style.COLOR_TEXT_SECONDARY
    code_bg   = "#F0F0EE"

    parts = [
        f"<p>At x = <b>{_fmt(step.x_n)}</b>, "
        f"f(x) = <b>{_fmt(step.f_xn)}</b>. "
        f"{_sign_sentence(step.f_xn)}</p>"
    ]

    if step.df_near_zero:
        parts.append(
            f"<p style='color:{style.COLOR_WARN_FG};'>"
            f"⚠ The derivative is very small "
            f"(f′(x) = {_fmt(step.df_xn, sig=3)}). "
            "This can cause a large step and may slow convergence.</p>"
        )

    if step.x_next is not None and step.df_xn != 0.0:
        parts.append(
            f"<p>The tangent slope is f′(x) = <b>{_fmt(step.df_xn)}</b>. "
            "Following the tangent to the x-axis:</p>"
        )

        n1 = idx + 1
        formula_html = (
            f"<p style='font-family:Consolas,monospace; "
            f"font-size:{style.SIZE_FORMULA}pt; "
            f"background:{code_bg}; padding:8px 12px; "
            f"border-radius:5px; margin:4px 0; "
            f"border-left:3px solid {style.COLOR_ACCENT};'>"
            f"x<sub>{n1}</sub> = x<sub>{idx}</sub>"
            f" &minus; f(x<sub>{idx}</sub>) / f′(x<sub>{idx}</sub>)<br>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= {_fmt(step.x_n)}"
            f" &minus; {_fmt(step.f_xn)} / {_fmt(step.df_xn)}<br>"
            f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= <b>{_fmt(step.x_next)}</b>"
            f"</p>"
        )
        parts.append(formula_html)
        parts.append(
            f"<p style='color:{sec_color};'>"
            f"The approximation moved by {_fmt(step.step_size)}.</p>"
            f"<p style='color:{sec_color};'>"
            f"<i>Look at the graph: the orange line is the tangent. "
            f"It crosses the x-axis at x = {_fmt(step.x_next)}, "
            "which becomes the next guess.</i></p>"
        )

    return "".join(parts)


def build_result_badge_html(result: NewtonResult) -> tuple[str, str]:
    """Return (html_text, kind) for the status badge.

    kind is 'success', 'warn', or 'error'.
    """
    sc = result.stop_code

    if result.converged:
        root_str = f"{result.root:.10g}" if result.root is not None else "—"
        n = len(result.steps)
        return (
            f"✓  Root found: x ≈ {root_str}<br>"
            f"after {n} iteration(s)",
            "success",
        )

    if sc == StopCode.MAX_ITERATIONS_REACHED:
        best = result.best_x
        best_str = f"{best:.8g}" if best is not None else "—"
        return (
            f"⚠  Did not converge in {len(result.steps)} iteration(s).<br>"
            f"Best approximation: x ≈ {best_str}",
            "warn",
        )

    if sc == StopCode.ZERO_DERIVATIVE:
        return "✗  f′(x) = 0 — tangent is horizontal, cannot continue.", "error"

    if sc == StopCode.DIVERGENCE_SUSPECTED:
        return "✗  Divergence detected — try a different starting point.", "error"

    if sc == StopCode.DOMAIN_ERROR:
        return f"✗  Domain error: {result.message}", "error"

    if sc == StopCode.NON_FINITE_VALUE:
        return "✗  Non-finite value encountered — function blows up near x₀.", "error"

    return f"✗  {result.message}", "error"
