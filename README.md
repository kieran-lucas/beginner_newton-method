# Newton's Method Explorer

Newton's Method Explorer is a small desktop learning app that visualizes Newton's method one iteration at a time. It is designed for beginners who want to understand what the tangent line is doing, why each approximation changes, and how the method eventually converges or fails.

## Preview

![Newton's Method Explorer app preview](./assets/screenshot.png)

## Features

- Type a function such as `x**2 - 2`, `cos(x) - x`, or `x**3 - x - 2`.
- Choose an initial guess `x0`.
- See each Newton iteration on an interactive graph.
- Follow the tangent line from the current point to the x-axis.
- Inspect the iteration table with `x_n`, `f(x_n)`, `f'(x_n)`, `x_(n+1)`, and step size.
- Read a plain-English explanation for the selected step.
- Try built-in presets for common convergence and failure cases.
- Adjust tolerance, maximum iterations, and graph range from the advanced controls.

## Why This Exists

Newton's method is often taught as a formula:

```text
x_(n+1) = x_n - f(x_n) / f'(x_n)
```

That formula is useful, but it can feel abstract. This app connects the formula to the geometry: the current point, the derivative slope, the tangent line, and the next approximation.

## Requirements

- Python 3.11 or later
- pip

## Installation

```bash
git clone https://github.com/kieran-lucas/beginner_newton-method.git
cd beginner_newton-method

python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

The app opens a desktop window. The minimum supported window size is `1020 x 680`.

## Run Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the test suite:

```bash
pytest tests/
```

## Tech Stack

- PyQt6 for the desktop interface
- Matplotlib for the graph canvas
- SymPy for expression parsing and derivatives
- pytest for automated tests

## Project Structure

```text
beginner_newton-method/
|-- main.py
|-- app/
|   |-- expression.py
|   |-- explanation.py
|   |-- newton.py
|   |-- plot.py
|   |-- presets.py
|   |-- style.py
|   |-- window.py
|   `-- panels/
|       |-- input_panel.py
|       |-- status_panel.py
|       `-- table_panel.py
|-- assets/
|   `-- screenshot.png
|-- docs/
|   `-- ux-spec.md
|-- tests/
|   |-- test_expression.py
|   `-- test_newton.py
|-- requirements.txt
|-- requirements-dev.txt
`-- ROADMAP.md
```

## Status

The core learning workflow is implemented:

- numerical Newton iteration
- expression parsing
- graph and tangent visualization
- step table
- explanation panel
- convergence and failure diagnostics
- preset examples

Packaging and export features are not configured yet. For now, the app runs directly from source.
