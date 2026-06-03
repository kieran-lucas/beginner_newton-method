# UX Architecture & Screen Design Specification
# Newton's Method Explorer — Desktop App

---

## 1. Product Positioning

This app is a **numerical-method learning simulator**, not a root-finding calculator. The primary question it answers is:

> "Why did Newton's method move the approximation from here to there?"

A user who types `x**2 - 2` and presses Run should come away understanding the tangent-line geometry of the method, not just seeing the number `1.41421356`.

**Personality:** Clean, academic, precise. The aesthetic should evoke a well-typeset textbook or a university numerical-methods handout — not a consumer app, not a toy calculator, not a "modern SaaS dashboard."

**Primary audience:** Students encountering Newton's method for the first time. Secondary audience: anyone who wants to develop intuition about convergence, divergence, or starting-point sensitivity.

---

## 2. Visual Hierarchy

Priority order — what the eye should land on first:

```
1. Plot canvas          ← the geometry IS the lesson
2. Explanation panel    ← plain English for the selected step
3. Iteration table      ← supporting data, not the star
4. Controls             ← needed but never the focus
```

The plot canvas must be the largest element on screen at all times. A user should never have to scroll to see it.

---

## 3. Main Window Layout

Minimum window size: **1000 × 680 px**  
Default window size: **1200 × 780 px**  
Window title: `Newton's Method — f(x) = x² – 2` (updates on each run)

### 3.1 Top-Level Split

The window is divided into two resizable columns via a `QSplitter(Horizontal)`:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Newton's Method Explorer                                 [─] [□] [×]    │
├────────────────────┬─────────────────────────────────────────────────────┤
│                    │                                                      │
│   LEFT SIDEBAR     │              RIGHT MAIN AREA                        │
│   (320 px default, │                                                      │
│    min 260 px)     │   ┌──────────────────────────────────────────────┐  │
│                    │   │                                              │  │
│  ┌──────────────┐  │   │                                              │  │
│  │              │  │   │           PLOT CANVAS                        │  │
│  │   CONTROLS   │  │   │           (~60% of right column height)      │  │
│  │              │  │   │                                              │  │
│  └──────────────┘  │   │                                              │  │
│                    │   │                                              │  │
│                    │   └──────────────────────────────────────────────┘  │
│  ┌──────────────┐  │   ┌──────────────────────────────────────────────┐  │
│  │              │  │   │                                              │  │
│  │  EXPLANATION │  │   │          ITERATION TABLE                     │  │
│  │  + STATUS    │  │   │          (~40% of right column height)       │  │
│  │              │  │   │                                              │  │
│  └──────────────┘  │   └──────────────────────────────────────────────┘  │
└────────────────────┴─────────────────────────────────────────────────────┘
```

The right column is itself a `QSplitter(Vertical)` between plot and table. Both splitters are user-draggable.

---

## 4. Region Specifications

### 4.1 Controls Panel (top of left sidebar)

Widget: `QFrame` with a subtle 1px border-bottom separator.

#### Always-visible (beginner) controls:

```
  f(x) =
  ┌────────────────────────────────┐
  │  x**2 - 2                      │  ← QLineEdit, monospace font
  └────────────────────────────────┘
  f'(x) = 2·x   [auto-computed]       ← read-only QLabel, secondary color

  x₀  ┌──────────────┐
      │  1.0          │               ← QLineEdit, numeric validator
      └──────────────┘

  ┌────────────────┐  ┌─────────────┐
  │  ▶  Run        │  │  ⟳  Reset   │  ← QPushButton, accent / neutral
  └────────────────┘  └─────────────┘

  ┌───────────────────────────────────┐
  │  ◀ Prev    Step 0 / —    Next ▶   │  ← step navigator, disabled until run
  └───────────────────────────────────┘

  ──────────── Examples ────────────
  ┌──────────────────────────────┐
  │  Select an example...      ▼ │    ← QComboBox
  └──────────────────────────────┘
```

**Function field behavior:**
- On edit: clear any previous run result, show neutral state
- On parse error (real-time, debounced 400 ms): show red underline + inline error label below field
- On successful parse: show `f'(x) = …` derived formula in secondary text
- Pressing Enter in the field triggers Run

**x₀ field behavior:**
- Accepts float notation: `1`, `1.0`, `-0.5`, `1e2`
- Red border on non-numeric input
- Does not accept empty; placeholder text: `e.g. 1.0`

**Run button:**
- Primary action; accent color (`#2B5EA7`)
- Becomes disabled (grayed) while any computation is running
- After run: label stays "Run" (re-running replaces the current result)

**Reset button:**
- Clears the plot to curve-only, deselects all table rows, resets explanation panel to idle state
- Does NOT clear the function or x₀ fields

**Step navigator:**
- Disabled until a successful run completes
- `◀ Prev` at step 0 is grayed
- `Next ▶` at the final step is grayed
- Center label: `Step 2 / 4` — updates on every change
- Keyboard: left/right arrow keys also navigate when the window has focus

#### Advanced controls (collapsed by default):

Triggered by a `▸ Advanced` disclosure triangle (`QToolButton` with `setCheckable`):

```
  ▾ Advanced
  ──────────────────────────────────
  Tolerance     [  1e-8  ]
  Max iterations [  50   ]
  x-axis range   [ -5  ] to [ 5  ]
  ☐  Show all tangent lines (faded)
  ☐  Animate steps  Speed [──●──]
```

- Tolerance and max iterations: validated QLineEdit (float / int)
- x-axis range: two QLineEdit fields; if left blank, the canvas auto-scales to center `x₀` with a ±4 unit window
- "Show all tangent lines": draws every iteration's tangent in a faded color on the plot; useful for seeing the full convergence path
- "Animate steps": auto-advances through steps with a configurable delay (QSlider, 200 ms – 2000 ms)

---

### 4.2 Explanation Panel (bottom of left sidebar)

Widget: `QScrollArea` wrapping a `QLabel` (rich text / HTML).

This panel is the voice of the app. It speaks to the user in plain English, one step at a time.

**Idle state (before first run):**
```
  Enter a function and an initial guess,
  then press Run to begin.

  Newton's method finds a root of f(x)
  by following the tangent line at each
  approximation to the x-axis.
```

**Mid-iteration state (step n selected):**
```
  Step 2 of 4

  At x = 1.500000, f(x) = 0.250000.
  The function is still above zero here.

  The tangent line at this point has
  slope f'(x) = 3.000000.

  Using the formula:
    x₃ = x₂ − f(x₂) / f'(x₂)
       = 1.5 − 0.25 / 3.0
       = 1.416667

  The approximation moved left by 0.083333.
```

**Status badge — converged (below explanation text):**
```
  ┌───────────────────────────────────┐
  │ ✓  Root found                     │  ← green background
  │    x ≈ 1.41421356                 │
  │    4 iterations  |  tol = 1×10⁻⁸  │
  └───────────────────────────────────┘
```

**Status badge — failure (replaces converged badge):**

| Failure type | Badge color | Message |
|---|---|---|
| Max iterations exceeded | Amber `#E8A020` | "Did not converge in 50 steps. Try a starting point closer to the root." |
| Zero derivative | Red `#C0392B` | "f'(x) = 0 at step 3. The tangent is horizontal — the method cannot continue." |
| Divergence | Red `#C0392B` | "The approximations are growing without bound. Choose a different starting point." |
| Oscillation | Amber `#E8A020` | "The method is cycling between two values. Try a starting point further from the local extremum." |
| Parse error | Red `#C0392B` | "Could not parse the expression. Check for balanced parentheses and valid syntax." |

**Display rules:**
- The formula line (`x_{n+1} = x_n − f(x_n)/f'(x_n) = …`) always shows the numeric substitution for the selected step — not just the abstract formula.
- All numbers in the explanation are shown to 6 significant figures for readability.
- The badge is always visible, even when scrolling the explanation text. Pin it to the bottom of the panel.

---

### 4.3 Plot Canvas (top of right column)

Widget: `FigureCanvasQTAgg` from Matplotlib, embedded in a `QWidget`.

#### Fixed elements (always visible):

- The curve `f(x)` plotted in dark navy (`#1A3C6E`), linewidth 2.0
- x-axis and y-axis, drawn as thin dark lines (not the default matplotlib spines — replace with explicit `axhline/axvline` at 0)
- Grid: very light gray (`#EBEBEB`), major gridlines only, no minor ticks
- Plot background: white (`#FFFFFF`)
- Figure background: matches app background (`#F7F7F5`)
- Axis labels: `x` and `f(x)`, small, secondary color

#### Per-iteration elements (updated when step changes):

| Element | Description | Style |
|---|---|---|
| Current point | Filled circle at `(x_n, f(x_n))` | Black dot, radius 5 |
| Tangent line | Line through `(x_n, f(x_n))` with slope `f'(x_n)`, clipped to view | Orange-rust `#D45F2A`, linewidth 1.5, dashed |
| Drop line | Vertical dashed line from `(x_n, f(x_n))` down to x-axis | Light gray, linewidth 1, dashed |
| Next point marker | Open circle on x-axis at `x_{n+1}` | Orange-rust outline, no fill |
| Annotation | Small label `x₁`, `x₂`, etc. at each x-axis marker | 9pt, secondary color |

#### Final-state element (shown after convergence):

- Filled green circle at `(x_root, 0)` with label `root ≈ 1.4142`

#### "Show all tangent lines" mode:

- All previous steps' tangent lines drawn in the same orange-rust but at 20% opacity
- Only the selected step's tangent is at full opacity

#### Auto-scaling rules:

- x-range default: `[x₀ − 4, x₀ + 4]`, adjusted to keep all iterated x values visible
- If any `x_n` falls outside the range, extend range by 20% on the appropriate side
- y-range: auto-scale from the function values in the visible x-range, clamped to `[-30, 30]` to prevent extreme functions from collapsing the view
- If the function evaluates to very large values (> 30) at the initial guess, show a warning label on the plot: "f(x₀) is large — zoom out or pick a closer starting point"

#### Toolbar:

A minimal toolbar below the canvas (Matplotlib's NavigationToolbar2QT, reduced): only **Pan**, **Zoom**, and **Home** buttons. Remove the "Save figure" button — that belongs to the app's own export action.

---

### 4.4 Iteration Table (bottom of right column)

Widget: `QTableWidget`, read-only, single-row selection.

#### Columns:

| Column | Header | Alignment | Width | Format |
|---|---|---|---|---|
| n | `n` | Center | 40 px | Integer |
| x_n | `xₙ` | Right | 120 px | 8 significant figures, monospace |
| f(x_n) | `f(xₙ)` | Right | 110 px | 6 sig figs, monospace |
| f'(x_n) | `f′(xₙ)` | Right | 110 px | 6 sig figs, monospace |
| x_next | `xₙ₊₁` | Right | 120 px | 8 sig figs, monospace |
| step_size | `\|step\|` | Right | 100 px | Scientific notation if < 0.001 |
| status | `status` | Center | 90 px | Text label (see below) |

#### Status column values:

| Condition | Label | Cell background |
|---|---|---|
| Running / in progress | `—` | White |
| Converged (final row) | `converged` | `#E8F5E9` (light green) |
| Max iterations (final row) | `max iter` | `#FFF8E1` (light amber) |
| Zero derivative | `f′=0` | `#FFEBEE` (light red) |
| Diverged | `diverged` | `#FFEBEE` (light red) |

#### Behavior:

- Clicking a row: selects the step, updates the plot to show that step's tangent, updates the explanation panel
- Selected row highlight: `#EBF0FA` (light blue-gray), not the system default blue
- The current step (as controlled by the step navigator) is always kept in sync with the selected table row
- After run: table scrolls to row 0, step 0 is selected
- Table header is non-interactive (no sorting — order is always chronological)
- Row height: 24 px (compact but readable)
- Horizontal scrollbar: auto (appears only if window is very narrow)

---

### 4.5 Preset / Examples Selector

Widget: `QComboBox` in the controls panel.

Selecting a preset immediately populates the function field, x₀, tolerance, and max iterations. It does NOT automatically run — the user must press Run. This gives them a moment to read the function before computation starts.

#### Built-in presets:

| Label | f(x) | x₀ | Expected behavior |
|---|---|---|---|
| Square root of 2 | `x**2 - 2` | `1.0` | Converges in 4 steps — ideal for first exploration |
| Cube root of 2 | `x**3 - 2` | `1.5` | Converges in ~5 steps |
| Dottie number | `cos(x) - x` | `1.0` | Converges smoothly (~6 steps) |
| Slow convergence | `x**3 - 2*x + 2` | `2.0` | Converges but takes more steps |
| Bad starting point | `x**3 - 2*x + 2` | `0.0` | Diverges — teaching failure case |
| Zero derivative trap | `x**3 - 3*x + 2` | `1.0` | f'(x₀) = 0, immediate failure |

The last two presets are grouped under a non-selectable separator label: `── Failure / Edge Cases ──`.

After selecting a preset, the combobox label updates to show the preset name. If the user then edits any field manually, the combobox reverts to `Select an example...`.

---

## 5. Interaction Model

### 5.1 User Flow — Happy Path

```
1. Launch app
   → Window opens showing the plot canvas area (empty, axes only)
   → Controls panel shows default values: f(x) = x**2 - 2, x₀ = 1.0
   → Explanation panel shows idle hint text

2. User types a function (or selects preset)
   → While typing: real-time parse attempt, debounced 400 ms
   → On valid parse: f'(x) formula appears below field
   → On invalid parse: red underline, inline error message

3. User presses Run (or Enter in function field)
   → Computation runs synchronously (Newton's method is fast)
   → Plot canvas draws the curve
   → Step 0 (the initial guess) is highlighted on plot and in table
   → Explanation panel shows step 0 description
   → Step navigator shows "Step 0 / N"
   → Status badge shows result (converged / failure)

4. User steps through iterations
   → Each press of Next ▶ advances one step
   → Plot redraws tangent for the new step
   → Table row selection moves to the new step
   → Explanation text updates
   → Animation mode: steps advance automatically

5. User selects any table row
   → Equivalent to clicking Next/Prev to that step number
   → Plot, explanation, and navigator all sync

6. User presses Reset
   → Plot returns to curve-only
   → Table clears
   → Explanation returns to idle
   → Step navigator disables
   → Function and x₀ fields retain their values
```

### 5.2 Animation Mode

When "Animate steps" is checked in Advanced:
- Pressing Run automatically advances through all steps at the configured speed
- A **Pause** button replaces the step navigator during animation
- After the final step, animation stops; controls return to normal
- The user can still click table rows to jump to any step after animation completes

### 5.3 Keyboard Shortcuts

| Key | Action |
|---|---|
| `Enter` (in function or x₀ field) | Run |
| `→` / `→` arrow | Next step |
| `←` arrow | Previous step |
| `Space` | Toggle play/pause animation |
| `R` | Reset |
| `Ctrl+S` | Save plot as PNG |

---

## 6. Error States

### 6.1 Parse Error (function field)

Trigger: SymPy cannot parse the expression.

Response:
- Red 1px bottom border on the function field
- Inline error label below the field (small, red text): `Could not parse expression — check for typos`
- The `f'(x)` line disappears
- Run button becomes disabled
- No crash, no dialog box

Recovery: fix the expression → error clears automatically on next valid parse.

### 6.2 Zero Derivative at x₀

Trigger: `f'(x₀) = 0` on the very first step.

Response:
- The table shows one row: step 0, with `f′=0` in the status column
- Explanation panel: "The derivative f'(x) = 0 at your starting point x = 1.0. The tangent line is horizontal and never crosses the x-axis. Newton's method cannot start from here. Try a different starting point."
- Status badge: red, "f′(x₀) = 0 — cannot start"
- Plot: shows the curve, marks x₀, draws the horizontal tangent line (so the user can see the geometry)

### 6.3 Zero Derivative Mid-Iteration

Trigger: `f'(x_n) = 0` at step n > 0.

Response:
- Table shows all rows up to and including step n, with `f′=0` on row n
- Method stops at step n
- Explanation: "At step n, the tangent becomes horizontal (f'(x) = 0). The method cannot continue from here."
- Status badge: red
- Plot shows all tangent lines up to step n; the horizontal tangent is drawn in red

### 6.4 Divergence

Trigger: `|x_n| > 1×10⁸` or step size grows by more than 2× for 3 consecutive steps.

Response:
- Table shows up to and including the detected-divergent step (max 20 rows displayed, then truncated with "… (diverging)")
- Explanation: "The approximations are moving away from any root. This often happens when the starting point is near a local extremum of f(x). The tangent line 'overshoots' further each step."
- Status badge: red
- Plot: if x values stay within the visible range, they are shown; if they exit the range, the plot adds an arrow annotation pointing off-screen

### 6.5 Oscillation

Trigger: `|x_n − x_{n-2}| < 1×10⁻¹⁰` and `|x_n − x_{n-1}| > 1×10⁻⁴` (cycling without converging).

Response:
- Table shows all rows; final row gets status `oscillating`
- Explanation: "The method is cycling between two approximations without converging. This typically occurs near a point where the curve has a local shape that causes the tangent to 'bounce.' Try a starting point further from this region."
- Status badge: amber

### 6.6 Max Iterations Exceeded

Trigger: iteration count reaches `max_iter` without meeting the tolerance condition.

Response:
- Table shows all `max_iter` rows
- Status badge: amber, "Did not converge in N steps"
- Explanation: "The method ran for the maximum number of steps without reaching a root within the specified tolerance. The best approximation found is x ≈ [last x_n]. Consider increasing max iterations or using a closer starting point."

### 6.7 Non-Real Result

Trigger: SymPy evaluates the function and gets a complex number at the initial guess.

Response:
- Inline error below function field: "f(x₀) is complex — this app handles real-valued functions only"
- Run button disabled

---

## 7. Visual Design Specification

### 7.1 Color Palette

| Token | Hex | Usage |
|---|---|---|
| `color-bg` | `#F7F7F5` | App and figure background |
| `color-surface` | `#FFFFFF` | Panel backgrounds, plot background |
| `color-border` | `#DDDDD8` | Panel separators, field borders |
| `color-text-primary` | `#1A1A1A` | Main text, axis labels |
| `color-text-secondary` | `#6B6B6B` | Labels, derived formula, column headers |
| `color-text-disabled` | `#B0B0B0` | Disabled controls |
| `color-accent` | `#2B5EA7` | Run button, selected highlights |
| `color-accent-hover` | `#1E4585` | Run button hover |
| `color-curve` | `#1A3C6E` | f(x) curve on plot |
| `color-tangent` | `#D45F2A` | Active tangent line |
| `color-tangent-faded` | `#D45F2A26` | Previous tangent lines (10% opacity) |
| `color-point` | `#1A1A1A` | Current point marker |
| `color-root` | `#2D7A2D` | Root marker (final converged point) |
| `color-success-bg` | `#E8F5E9` | Converged badge background |
| `color-success-fg` | `#1B5E20` | Converged badge text |
| `color-warn-bg` | `#FFF8E1` | Slow convergence / max iter badge |
| `color-warn-fg` | `#795548` | Warning badge text |
| `color-error-bg` | `#FFEBEE` | Failure badge background |
| `color-error-fg` | `#B71C1C` | Failure badge text |
| `color-row-selected` | `#EBF0FA` | Selected table row |

### 7.2 Typography

| Context | Font | Size | Weight |
|---|---|---|---|
| Function input field | Monospace (Consolas → Courier New → system mono) | 13pt | Regular |
| Derived formula label | Monospace | 11pt | Regular |
| Table number cells | Monospace | 10pt | Regular |
| Table header | System sans-serif | 10pt | SemiBold |
| Explanation text | System sans-serif | 10pt | Regular |
| Step label in navigator | System sans-serif | 10pt | Regular |
| Status badge text | System sans-serif | 10pt | SemiBold |
| Button labels | System sans-serif | 10pt | Regular |
| Section separators | System sans-serif | 9pt | SemiBold, uppercase, `color-text-secondary` |

Line height for explanation text: 1.5× font size.

### 7.3 Spacing

| Element | Value |
|---|---|
| Outer window margin | 0 (panels flush to edge) |
| Sidebar inner padding | 16 px horizontal, 12 px vertical |
| Between control groups | 12 px gap |
| Between label and field | 4 px |
| Button height | 32 px |
| Table row height | 24 px |
| Status badge padding | 10 px horizontal, 8 px vertical |
| Section separator margin | 8 px top + bottom |

### 7.4 Animation

- Step transition: redraw the plot in a single repaint — no tweening, no frame-based animation of the tangent line. The geometry must update instantly when the user selects a step.
- "Animate steps" mode: timer-based step advancement using `QTimer`. The delay is configurable via the speed slider. No visual motion between steps — each tick is an instant state update.
- No other animation in the app. No fade transitions, no progress spinners, no loading states (Newton's method computes in microseconds).

### 7.5 Layout Grid

Qt stylesheet approach: use `QWidget` stylesheets for colors and padding. Use `QVBoxLayout` / `QHBoxLayout` for all layout. No absolute positioning. All font and color constants defined in a single `app/style.py` module as Python constants so they can be changed in one place.

---

## 8. Beginner vs Advanced Separation

| Feature | Visibility | Rationale |
|---|---|---|
| f(x) input | Always visible | Core action |
| x₀ input | Always visible | Core action |
| Run / Reset | Always visible | Core action |
| Step navigator | Always visible (disabled until run) | Core teaching interaction |
| Presets dropdown | Always visible | Beginner entry point |
| f'(x) formula display | Always visible (read-only) | Teaching aid — shows the derivative without requiring user knowledge of calculus |
| Tolerance | Advanced (collapsed) | Default `1e-8` is correct for all beginner use cases |
| Max iterations | Advanced (collapsed) | Default `50` is fine |
| x-axis range | Advanced (collapsed) | Auto-scale handles the common case |
| Show all tangents | Advanced (collapsed) | Useful for advanced exploration, clutters beginner view |
| Animate speed | Advanced (collapsed) | Secondary feature |

The Advanced section **opens automatically** if a parse error or convergence failure occurred due to a setting — e.g., if max iterations is likely the cause, highlight the field in the Advanced panel.

---

## 9. Idle / Empty State

When the app first launches (before any run):
- Plot canvas: draw only the x and y axes, no curve. Show a centered hint: "Enter a function above and press Run."
- Iteration table: empty with dimmed column headers
- Explanation panel: introductory text (as specified in 4.2)
- Step navigator: disabled
- Status badge: not shown

This makes the purpose of each region immediately obvious even before the user has done anything.

---

## 10. What the App Does NOT Do

These are deliberate exclusions to keep scope focused:

- No multiple simultaneous functions
- No complex-number roots
- No other root-finding methods (bisection, secant) — this is specifically Newton's method
- No 3D plots
- No symbolic root verification (the app shows the numerical process, not the algebraic solution)
- No saving/loading sessions
- No dark mode (not in v1)
- No mobile or web version
