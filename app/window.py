from __future__ import annotations

from dataclasses import asdict

from PyQt6.QtWidgets import QMainWindow, QWidget, QSplitter, QVBoxLayout
from PyQt6.QtCore import Qt

from app import explanation, style
from app.expression import parse_expression
from app.newton import IterationRecord, NewtonResult, StopCode, newton_iterate
from app.panels.input_panel import InputPanel
from app.panels.status_panel import StatusPanel
from app.panels.table_panel import TablePanel
from app.plot import PlotCanvas


class MainWindow(QMainWindow):
    """Top-level window.

    Layout (QSplitter H):
        left  → QSplitter V:  InputPanel  /  StatusPanel
        right → QSplitter V:  PlotCanvas  /  TablePanel

    Run flow:
        1. InputPanel emits run_requested(expr, x0)
        2. _on_run parses, computes, stores result, updates all panels
        3. InputPanel step navigator / table row click → _show_step(idx)
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Newton's Method Explorer")
        self.setMinimumSize(style.WINDOW_MIN_W, style.WINDOW_MIN_H)
        self.resize(style.WINDOW_DEFAULT_W, style.WINDOW_DEFAULT_H)

        self._result: NewtonResult | None = None

        self._build_layout()
        self._connect_signals()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        h_split = QSplitter(Qt.Orientation.Horizontal)
        h_split.setChildrenCollapsible(False)

        # Left sidebar
        left = QWidget()
        left.setMinimumWidth(style.SIDEBAR_MIN_WIDTH)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.input_panel  = InputPanel()
        self.status_panel = StatusPanel()

        left_vsplit = QSplitter(Qt.Orientation.Vertical)
        left_vsplit.setChildrenCollapsible(False)
        left_vsplit.addWidget(self.input_panel)
        left_vsplit.addWidget(self.status_panel)
        left_vsplit.setSizes([370, 310])
        left_layout.addWidget(left_vsplit)

        # Right main area
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.plot_canvas = PlotCanvas()
        self.table_panel = TablePanel()

        right_vsplit = QSplitter(Qt.Orientation.Vertical)
        right_vsplit.setChildrenCollapsible(False)
        right_vsplit.addWidget(self.plot_canvas)
        right_vsplit.addWidget(self.table_panel)
        right_vsplit.setSizes([460, 220])
        right_layout.addWidget(right_vsplit)

        h_split.addWidget(left)
        h_split.addWidget(right)
        h_split.setSizes([
            style.SIDEBAR_DEFAULT_WIDTH,
            style.WINDOW_DEFAULT_W - style.SIDEBAR_DEFAULT_WIDTH,
        ])

        root.addWidget(h_split)

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self.input_panel.run_requested.connect(self._on_run)
        self.input_panel.reset_requested.connect(self._on_reset)
        self.input_panel.step_changed.connect(self._on_step_changed)
        self.table_panel.step_selected.connect(self._on_table_step_selected)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_run(self, expr: str, x0: float) -> None:
        # 1. Parse expression
        try:
            f, df, f_str, df_str = parse_expression(expr)
        except ValueError as exc:
            self.input_panel.set_parse_error(str(exc))
            self.status_panel.set_explanation(
                f"<p style='color:{style.COLOR_ERROR_FG};'>"
                f"<b>Parse error:</b> {exc}</p>"
                "<p>Check the function for typos, unbalanced parentheses, "
                "or unsupported symbols.</p>"
            )
            return

        self.input_panel.set_parse_error("")
        self.input_panel.set_derivative_label(df_str)

        # 2. Run Newton
        tol      = self.input_panel.get_tolerance()
        max_iter = self.input_panel.get_max_iter()
        x_range  = self.input_panel.get_x_range()

        try:
            result = newton_iterate(f, df, x0, tol=tol, max_iter=max_iter)
        except ValueError as exc:
            self.status_panel.set_explanation(
                f"<p style='color:{style.COLOR_ERROR_FG};'>"
                f"<b>Invalid parameters:</b> {exc}</p>"
            )
            return

        # 3. Store result
        self._result = result
        self.setWindowTitle(f"Newton's Method Explorer — f(x) = {expr}")

        # 4. Compute x_range if not overridden
        if x_range is None:
            x_range = self._auto_x_range(x0, result.steps)

        # 5. Update panels
        self.plot_canvas.new_run(f, result.steps, x_range)

        steps_dicts = [asdict(s) for s in result.steps]
        self.table_panel.load_steps(steps_dicts)

        last_idx = len(result.steps) - 1
        self.input_panel.set_step_state(0, last_idx)
        self.table_panel.select_row(0)

        self._show_step(0)
        badge_html, badge_kind = explanation.build_result_badge_html(result)
        self.status_panel.set_badge(badge_html, badge_kind)

    def _on_reset(self) -> None:
        self._result = None
        self.setWindowTitle("Newton's Method Explorer")
        self.plot_canvas.reset()
        self.table_panel.clear()
        self.status_panel.set_idle()
        self.input_panel.reset_navigator()
        self.input_panel.set_derivative_label("—")

    def _on_step_changed(self, idx: int) -> None:
        if self._result and idx < len(self._result.steps):
            self.table_panel.select_row(idx)
            self._show_step(idx)

    def _on_table_step_selected(self, idx: int) -> None:
        if self._result and idx < len(self._result.steps):
            self.input_panel.set_step_state(idx, len(self._result.steps) - 1)
            self.plot_canvas.show_step(idx)
            self._update_explanation(idx)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _show_step(self, idx: int) -> None:
        self.plot_canvas.show_step(idx)
        self._update_explanation(idx)

    def _update_explanation(self, idx: int) -> None:
        if not self._result:
            return
        step  = self._result.steps[idx]
        total = len(self._result.steps)
        html  = explanation.build_step_html(step, idx, total, self._result)
        self.status_panel.set_explanation(html)

    @staticmethod
    def _auto_x_range(x0: float, steps: list[IterationRecord]) -> tuple[float, float]:
        xs = [x0]
        for s in steps:
            xs.append(s.x_n)
            if s.x_next is not None:
                xs.append(s.x_next)

        import math
        finite_xs = [v for v in xs if math.isfinite(v) and abs(v) < 1e7]
        if not finite_xs:
            return (x0 - 5.0, x0 + 5.0)

        lo, hi   = min(finite_xs), max(finite_xs)
        span     = max(hi - lo, 2.0)
        margin   = span * 0.30
        return (lo - margin, hi + margin)
