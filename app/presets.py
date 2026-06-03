"""Built-in example functions for the Newton's method visualiser.

Each preset includes educational metadata so the UI can show the user
what to look for before they even press Run.
"""

PRESETS: list[dict] = [
    {
        "label":       "Square root of 2  —  x² – 2",
        "expr":        "x**2 - 2",
        "x0":          1.0,
        "tol":         1e-8,
        "max_iter":    50,
        "is_edge_case": False,
        "title":       "Square root of 2",
        "explanation": (
            "A classic first example. Newton's method is being used to solve "
            "x² – 2 = 0, which finds √2 ≈ 1.41421356. "
            "The method converges very quickly — usually in just 4–5 steps."
        ),
        "observe": (
            "Watch how each tangent line crosses the x-axis closer to √2. "
            "The step size shrinks rapidly — this is quadratic convergence."
        ),
        "expected": "CONVERGED_RESIDUAL",
    },
    {
        "label":       "Cube root of 2  —  x³ – 2",
        "expr":        "x**3 - 2",
        "x0":          1.5,
        "tol":         1e-8,
        "max_iter":    50,
        "is_edge_case": False,
        "title":       "Cube root of 2",
        "explanation": (
            "Finds ∛2 ≈ 1.259921. The derivative f′(x) = 3x² is well-behaved "
            "away from zero, so convergence is fast and stable."
        ),
        "observe": (
            "Notice that the tangent lines approach the root from the same "
            "side each step, rather than oscillating."
        ),
        "expected": "CONVERGED_RESIDUAL",
    },
    {
        "label":       "Dottie number  —  cos(x) – x",
        "expr":        "cos(x) - x",
        "x0":          1.0,
        "tol":         1e-8,
        "max_iter":    50,
        "is_edge_case": False,
        "title":       "The Dottie number",
        "explanation": (
            "Finds the unique fixed point of cosine: cos(x) = x, "
            "known as the Dottie number ≈ 0.739085. "
            "If you keep pressing the cosine button on a calculator, "
            "it always converges to this value."
        ),
        "observe": (
            "The function crosses the x-axis at a slight angle, "
            "so convergence is smooth and consistent."
        ),
        "expected": "CONVERGED_RESIDUAL",
    },
    {
        "label":       "Double root — slow convergence  —  (x – 1)²",
        "expr":        "(x - 1)**2",
        "x0":          0.0,
        "tol":         1e-8,
        "max_iter":    80,
        "is_edge_case": False,
        "title":       "Double root (slow convergence)",
        "explanation": (
            "Near a repeated root, the derivative is also small, "
            "so Newton's method loses its quadratic convergence and "
            "becomes linear. The method still converges, but much more slowly."
        ),
        "observe": (
            "Each tangent line only makes small progress. "
            "Compare the step sizes here to the square-root example."
        ),
        "expected": "CONVERGED_RESIDUAL",
    },
    {
        "label":       "⚠  Domain-sensitive  —  ln(x) – 1",
        "expr":        "log(x) - 1",
        "x0":          3.0,
        "tol":         1e-8,
        "max_iter":    50,
        "is_edge_case": True,
        "title":       "ln(x) – 1 (domain-sensitive)",
        "explanation": (
            "Finds x where ln(x) = 1, i.e. x = e ≈ 2.71828. "
            "The function is only defined for x > 0 — a starting guess "
            "of x ≤ 0 would produce a domain error."
        ),
        "observe": (
            "A positive starting guess converges correctly. "
            "Try changing x₀ to a negative value to see the domain error."
        ),
        "expected": "CONVERGED_RESIDUAL",
    },
    {
        "label":       "⚠  Bad start → diverges  —  x³ – 2x + 2, x₀ = 0",
        "expr":        "x**3 - 2*x + 2",
        "x0":          0.0,
        "tol":         1e-8,
        "max_iter":    20,
        "is_edge_case": True,
        "title":       "Bad starting point (diverges)",
        "explanation": (
            "This starting point is near a local maximum of f(x). "
            "The derivative is very small, causing the tangent to overshoot "
            "wildly and the method to diverge."
        ),
        "observe": (
            "The tangent line at x = 0 is almost flat, so it crosses the "
            "x-axis far away. Each subsequent step moves further, not closer."
        ),
        "expected": "DIVERGENCE_SUSPECTED",
    },
    {
        "label":       "⚠  Zero derivative trap  —  x³ – 3x + 2, x₀ = 1",
        "expr":        "x**3 - 3*x + 2",
        "x0":          1.0,
        "tol":         1e-8,
        "max_iter":    50,
        "is_edge_case": True,
        "title":       "Zero derivative (immediate failure)",
        "explanation": (
            "At x = 1, f(x) = 0 and f′(x) = 3(1)² – 3 = 0 exactly. "
            "x = 1 is both a root AND a critical point. "
            "Newton's method fails at the very first step because the "
            "tangent line is horizontal."
        ),
        "observe": (
            "The tangent line is completely flat — it runs along y = 0 "
            "and never crosses the x-axis."
        ),
        "expected": "ZERO_DERIVATIVE",
    },
]
