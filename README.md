# Newton's Method Explorer

A beginner-friendly desktop app for visualising Newton's method step by step: initial guess, tangent line, next approximation, convergence, and failure cases.

![Newton's Method Explorer — Lexend UI, step 1 of 5 for f(x) = x² − 2 with tangent line, iteration table, and step-by-step explanation](assets/screenshot.png)

---

## What this app teaches

Newton's method finds a root of f(x) by drawing the tangent line at the current approximation and following it to the x-axis. This app shows **why** each approximation moved where it did — not just what the final answer is.

---

## Requirements

- Python 3.11 or later
- pip

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/kieran-lucas/beginner_newton-method.git
cd beginner_newton-method

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the app

```bash
python main.py
```

The window requires a minimum size of 1000 × 680 px.

---

## Developer setup

```bash
# Install development dependencies (adds pytest and pytest-qt)
pip install -r requirements-dev.txt
```

---

## Running tests

```bash
pytest tests/
```

---

## Build / package

Not yet configured.  The app runs directly from source with `python main.py`.

---

## Project structure

```
beginner_newton-method/
├── main.py                     entry point
├── app/
│   ├── style.py                colour tokens, font sizes, Qt stylesheet
│   ├── newton.py               numerical core  (Stage 2)
│   ├── expression.py           SymPy expression parser  (Stage 3)
│   ├── plot.py                 Matplotlib canvas widget  (Stage 4)
│   ├── window.py               MainWindow — assembles all panels
│   ├── presets.py              built-in example functions
│   └── panels/
│       ├── input_panel.py      function input, x₀, run/reset, step navigator
│       ├── table_panel.py      per-iteration data table
│       └── status_panel.py     plain-English explanation + result badge
├── tests/
│   └── test_newton.py
├── docs/
│   └── ux-spec.md              full UX architecture specification
├── ROADMAP.md                  10-stage implementation plan
├── requirements.txt
└── requirements-dev.txt
```

---

## Development status

| Stage | Description | Status |
|---|---|---|
| 1 | Project scaffold | ✅ Done |
| 2 | Newton numerical core | ✅ Done |
| 3 | Expression parsing (SymPy) | ✅ Done |
| 4 | Graph and tangent visualisation | ✅ Done |
| 5 | Iteration table and explanation panel | ✅ Done |
| 6 | Convergence / failure diagnostics | ✅ Done |
| 7 | Presets and examples | ✅ Done |
| 8 | Export and polish | ⬜ Not started |
| 9 | README and portfolio presentation | ✅ Done |
| 10 | Testing and validation | ⬜ Not started |
