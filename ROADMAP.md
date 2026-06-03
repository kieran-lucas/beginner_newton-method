# Implementation Roadmap — Newton's Method Desktop App

## Repository Audit (2026-06-03)

### Current State

| Item | Status |
|---|---|
| README | 2-line stub — no instructions |
| Source code | None |
| Build system | None |
| Language / framework | Not decided |
| Newton method logic | None |
| Plotting / visualization | None |
| Tests | None |
| Package metadata | None |

The repository contains only a README and git metadata. Nothing can be run. The project is a blank slate.

---

## Architecture Decision

**Stack: Python + PyQt6 + Matplotlib + SymPy**

| Component | Role |
|---|---|
| Python 3.11+ | Runtime |
| PyQt6 | Desktop GUI and window management |
| Matplotlib (Qt backend) | In-app plot canvas embedded in the Qt window |
| SymPy | Symbolic parsing of user-entered functions, analytic derivatives |
| pytest | Unit + integration testing |

**Why this stack:**
- PyQt6 is cross-platform, pip-installable, and produces a real native desktop window.
- Matplotlib embeds cleanly into Qt via `FigureCanvasQTAgg`; no browser or JS needed.
- SymPy computes the exact derivative of whatever function the user enters, eliminating finite-difference errors and making the tangent line mathematically precise.
- The entire stack is well-documented and beginner-readable.
- No compile step; `pip install` is sufficient.

**Module layout (target):**

```
beginner_newton-method/
├── main.py                  # entry point — creates QApplication, launches MainWindow
├── app/
│   ├── __init__.py
│   ├── newton.py            # pure numerical core: iterate(), tangent_line(), convergence check
│   ├── expression.py        # SymPy parsing and safe evaluation of user-entered functions
│   ├── plot.py              # Matplotlib canvas widget, draw_function(), draw_tangent(), draw_point()
│   ├── window.py            # MainWindow — assembles all widgets
│   ├── panels/
│   │   ├── input_panel.py   # function input, initial guess, max iterations, tolerance fields
│   │   ├── table_panel.py   # QTableWidget showing each iteration: x_n, f(x_n), f'(x_n), x_{n+1}
│   │   └── status_panel.py  # convergence/failure message, final root estimate
│   └── presets.py           # named example functions with known roots
├── tests/
│   ├── test_newton.py
│   ├── test_expression.py
│   └── test_convergence.py
├── assets/
│   └── (icons, if needed)
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Implementation Stages

### Stage 1 — Project Scaffold and Developer Workflow

**Goal:** A runnable (but empty) app window and a working dev environment.

**Files:**
- `main.py` — minimal `QApplication` + `MainWindow` show
- `app/__init__.py`, `app/window.py` — skeleton window
- `requirements.txt` — `PyQt6`, `matplotlib`, `sympy`
- `requirements-dev.txt` — `pytest`, `pytest-qt`
- `.gitignore` — Python standard ignore
- Updated `README.md` — how to install and run

**Expected output:** `python main.py` opens a blank window.

**Risks:**
- PyQt6 vs PyQt5 import paths differ; pin `PyQt6>=6.5`.
- On some systems Matplotlib's Qt backend requires `PyQt6` explicitly in the import path. Test early.

---

### Stage 2 — Newton Method Numerical Core

**Goal:** A pure-Python module that implements the iteration with no UI dependency.

**Files:** `app/newton.py`

**Key functions:**
- `newton_iterate(f, df, x0, tol, max_iter) -> list[dict]` — returns a list of step records, each with `x_n`, `f_xn`, `df_xn`, `x_next`, `step`
- `tangent_at(f, df, x) -> (slope, intercept)` — returns tangent line parameters at a given x
- Convergence detection: `|f(x_n)| < tol` or `|x_{n+1} - x_n| < tol`
- Failure detection: `df(x_n) == 0` (zero derivative), max iterations exceeded, oscillation/divergence flag

**Expected output:** `newton_iterate` returns correct step records for `f(x) = x^2 - 2`, `x0 = 1.0`.

**Risks:**
- Division-by-zero when `f'(x) = 0` must raise a typed exception, not crash.
- Divergence is harder to detect than non-convergence; a simple `|x_n| > 1e8` guard is sufficient for v1.

---

### Stage 3 — Function Input / Parsing / Safe Evaluation

**Goal:** Accept a string like `x**2 - 2` or `sin(x) - x/2`, parse it with SymPy, return callable `f` and `df`.

**Files:** `app/expression.py`

**Key functions:**
- `parse_expression(expr_str: str) -> (f: Callable, df: Callable, sym_expr, sym_deriv)` — returns both numeric callables and symbolic objects for display
- Error handling: `SympifyError`, `TypeError`, empty input, non-real results
- The symbolic derivative is displayed in the UI as a readable string (e.g., `f'(x) = 2x`)

**Expected output:** `parse_expression("x**2 - 2")` returns a callable `f` where `f(1.5)` returns `0.25`.

**Risks:**
- `sympify` with `locals` must block arbitrary Python (`__import__`, `os`, etc.). Use SymPy's safe parser (`parse_expr` with `transformations="all"` and a restricted namespace).
- Trig functions use radians; document this in the UI.

---

### Stage 4 — Graph and Tangent Visualization

**Goal:** A Matplotlib canvas embedded in Qt that plots `f(x)`, marks each iteration's x-point, and draws the tangent line for the selected step.

**Files:** `app/plot.py`

**Key methods on the canvas widget:**
- `plot_function(f, x_range)` — draw the curve
- `plot_iteration(step_record)` — mark x_n, draw tangent line from x_n to x_{n+1}, mark x_{n+1}
- `clear_iterations()` — reset to curve only
- `highlight_root(x_root)` — mark the final root

**Expected output:** After running `x^2 - 2` from `x=2.0`, the canvas shows the parabola, the first tangent line touching at `(2, 2)`, and the next x approximation at `x=1.5`.

**Risks:**
- Tangent line display range: extend the tangent line segment enough to be visible but not so far it dominates the plot. Clip to `x_range ± 20%`.
- Auto-scaling the y-axis when functions have large values can make tangent lines invisible. Clamp y-axis to `[-20, 20]` by default with an override.

---

### Stage 5 — Iteration Table and Explanation Panel

**Goal:** A QTableWidget that shows each step as a row, and a text panel that explains in plain English what happened in the selected step.

**Files:** `app/panels/table_panel.py`, `app/panels/status_panel.py`

**Table columns:** `n`, `x_n`, `f(x_n)`, `f'(x_n)`, `x_{n+1}`, `step size`

**Explanation panel text (per selected row):**
- "At x = 1.414, f(x) = 0.000004, which is close to zero."
- "The tangent line at this point has slope 2.828."
- "Following the tangent to the x-axis gives the next guess: x = 1.41421356."

**Expected output:** Clicking a row in the table updates the plot to that step's tangent and updates the explanation text.

**Risks:**
- Floating-point display precision: show 6 significant figures in the table, full precision in the explanation.
- Table row click → plot update → explanation update must be wired as a single Qt signal with no circular updates.

---

### Stage 6 — Convergence and Failure Diagnostics

**Goal:** Clearly communicate whether and why Newton's method succeeded or failed.

**Files:** additions to `app/panels/status_panel.py` and `app/newton.py`

**Cases to handle:**

| Case | User-visible message |
|---|---|
| Converged within tolerance | "Root found: x ≈ 1.41421 after 4 iterations." |
| Max iterations exceeded | "Did not converge in 50 iterations. Try a closer initial guess." |
| Zero derivative | "f'(x) = 0 at step 3 — Newton's method cannot continue (tangent is horizontal)." |
| Divergence detected | "The approximations are growing without bound. The method is diverging." |
| Oscillation detected | "The method is oscillating between two values. Try a different starting point." |

**Expected output:** Each failure case shows a colored status badge (red/orange) and a plain-English explanation.

**Risks:**
- Oscillation detection requires comparing `x_n` to `x_{n-2}`; a tolerance of `1e-10` prevents false positives from near-convergence noise.

---

### Stage 7 — Presets and Examples

**Goal:** A dropdown of pre-loaded examples so users can explore without typing.

**Files:** `app/presets.py`, additions to `app/panels/input_panel.py`

**Suggested presets:**

| Name | Expression | x₀ | Notes |
|---|---|---|---|
| Square root of 2 | `x**2 - 2` | 1.0 | Classic intro example |
| Cubic | `x**3 - x - 2` | 2.0 | Single real root |
| Trigonometric | `cos(x) - x` | 1.0 | Dottie number |
| Near-failure | `x**3 - 2*x + 2` | 0.0 | Bad starting point — diverges |
| Zero derivative trap | `x**3 - 3*x + 2` | 1.0 | f'(1) = 0, immediate failure |

**Expected output:** Selecting a preset fills all input fields and is ready to run.

**Risks:**
- Presets that intentionally fail must not crash the app — they are teaching moments.

---

### Stage 8 — Export / Share / Demo Polish

**Goal:** Allow users to save the plot as an image and copy the iteration table as text.

**Files:** additions to `app/window.py`

**Features:**
- "Save plot" button → `matplotlib savefig` PNG/PDF dialog
- "Copy table" button → copies CSV-formatted iteration data to clipboard
- Window title updates to show current function: "Newton's Method — f(x) = x² - 2"

**Expected output:** A saved PNG shows the function curve, tangent lines, and marked root.

**Risks:** None significant; keep this stage simple.

---

### Stage 9 — README and Portfolio Presentation

**Goal:** A README that explains what the app does, why it exists, how to install and run it, and includes a screenshot.

**Files:** `README.md`, `assets/screenshot.png`

**Sections:**
1. What is Newton's method? (2 sentences)
2. What does this app show? (features list)
3. Screenshot
4. Installation (3-step pip install + run)
5. Usage walkthrough (preset → run → click steps)
6. Known limitations
7. License

**Risks:** None.

---

### Stage 10 — Testing and Validation

**Goal:** Automated tests for the numerical core and expression parser.

**Files:** `tests/test_newton.py`, `tests/test_expression.py`, `tests/test_convergence.py`

**Test coverage targets:**

- `newton_iterate` on 5 known functions with known roots — check convergence and final value within `1e-9`
- All 5 failure cases produce the correct exception / termination code
- `parse_expression` on valid strings, invalid strings, dangerous strings, trig functions
- Oscillation and divergence detection produce correct flags

**Expected output:** `pytest tests/` passes with no failures.

**Risks:**
- Qt widgets cannot be tested headlessly without `pytest-qt` or a virtual display. Keep numerical core UI-independent so it can be tested without any Qt imports.

---

## Suggested Next Prompt

**Execute Stage 1:** Create the project scaffold — `main.py`, `app/` package skeleton, `requirements.txt`, `.gitignore`, and an updated README with installation instructions. The app should open a blank but titled Qt window when `python main.py` is run. No Newton logic yet.
