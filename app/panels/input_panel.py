from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QToolButton, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from app import style
from app.presets import PRESETS


class InputPanel(QWidget):
    """Controls panel: function input, x₀, run/reset, step nav, presets, advanced.

    Signals:
        run_requested(expr: str, x0: float)   — user pressed Run or Enter
        reset_requested()                      — user pressed Reset
        step_changed(index: int)               — step navigator moved
    """

    run_requested = pyqtSignal(str, float)
    reset_requested = pyqtSignal()
    step_changed = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("surface")
        self._step = 0
        self._total_steps = 0
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            style.PANEL_PADDING_H, style.PANEL_PADDING_V,
            style.PANEL_PADDING_H, style.PANEL_PADDING_V,
        )
        outer.setSpacing(style.SECTION_GAP)

        outer.addWidget(self._function_section())
        outer.addWidget(self._x0_section())
        outer.addWidget(self._run_controls())
        outer.addWidget(self._step_navigator())
        outer.addWidget(self._hr())
        outer.addWidget(self._presets_section())
        outer.addWidget(self._hr())
        outer.addWidget(self._advanced_section())
        outer.addStretch()

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {style.COLOR_TEXT_SECONDARY}; "
            f"font-family: '{style.FONT_UI}'; "
            f"font-size: {style.SIZE_SECTION_LABEL}pt; "
            f"font-weight: 700; letter-spacing: 1px;"
        )
        return lbl

    def _hr(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {style.COLOR_BORDER};")
        sep.setFixedHeight(1)
        return sep

    def _function_section(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        lay.addWidget(self._section_label("FUNCTION"))

        lbl = QLabel("f(x) =")
        lbl.setStyleSheet(f"color: {style.COLOR_TEXT_SECONDARY};")
        lay.addWidget(lbl)

        self.fx_input = QLineEdit()
        self.fx_input.setPlaceholderText("e.g.  x**2 - 2")
        self.fx_input.setText("x**2 - 2")
        mono = QFont("Consolas")
        mono.setStyleHint(QFont.StyleHint.TypeWriter)
        mono.setPointSize(style.SIZE_INPUT)
        self.fx_input.setFont(mono)
        self.fx_input.returnPressed.connect(self._on_run)
        self.fx_input.textEdited.connect(self._on_expr_edited)
        lay.addWidget(self.fx_input)

        self.deriv_label = QLabel("f′(x) = —")
        deriv_font = QFont(style.FONT_UI)
        deriv_font.setPointSize(style.SIZE_FORMULA)
        self.deriv_label.setFont(deriv_font)
        self.deriv_label.setStyleSheet(
            f"color: {style.COLOR_TEXT_SECONDARY}; font-style: italic;"
        )
        lay.addWidget(self.deriv_label)

        self.parse_error_label = QLabel()
        self.parse_error_label.setWordWrap(True)
        self.parse_error_label.setStyleSheet(
            f"color: {style.COLOR_ERROR_FG}; font-size: {style.SIZE_SMALL}pt;"
        )
        self.parse_error_label.setVisible(False)
        lay.addWidget(self.parse_error_label)

        return w

    def _x0_section(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        lay.addWidget(self._section_label("INITIAL GUESS"))

        row = QHBoxLayout()
        lbl = QLabel("x₀ =")
        lbl.setStyleSheet(f"color: {style.COLOR_TEXT_SECONDARY};")
        lbl.setFixedWidth(36)

        self.x0_input = QLineEdit()
        self.x0_input.setPlaceholderText("e.g. 1.0")
        self.x0_input.setText("1.0")
        self.x0_input.returnPressed.connect(self._on_run)

        row.addWidget(lbl)
        row.addWidget(self.x0_input)
        lay.addLayout(row)
        return w

    def _run_controls(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        self.btn_run = QPushButton("▶  Run")
        self.btn_run.setObjectName("btn_run")
        self.btn_run.setFixedHeight(style.BUTTON_H)
        self.btn_run.setToolTip("Run Newton's method (Enter)")
        self.btn_run.clicked.connect(self._on_run)

        self.btn_reset = QPushButton("⟳  Reset")
        self.btn_reset.setFixedHeight(style.BUTTON_H)
        self.btn_reset.setToolTip("Clear results")
        self.btn_reset.clicked.connect(self.reset_requested.emit)

        lay.addWidget(self.btn_run, stretch=2)
        lay.addWidget(self.btn_reset, stretch=1)
        return w

    def _step_navigator(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.btn_prev = QPushButton("◄ Prev")
        self.btn_prev.setEnabled(False)
        self.btn_prev.setFixedHeight(style.BUTTON_H)
        self.btn_prev.clicked.connect(self._on_prev)

        self.step_label = QLabel("Step — / —")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label.setStyleSheet(
            f"color: {style.COLOR_TEXT_SECONDARY}; "
            f"font-family: '{style.FONT_UI}'; font-weight: 500;"
        )

        self.btn_next = QPushButton("Next ►")
        self.btn_next.setEnabled(False)
        self.btn_next.setFixedHeight(style.BUTTON_H)
        self.btn_next.clicked.connect(self._on_next)

        lay.addWidget(self.btn_prev, stretch=1)
        lay.addWidget(self.step_label, stretch=2)
        lay.addWidget(self.btn_next, stretch=1)
        return w

    def _presets_section(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        lay.addWidget(self._section_label("EXAMPLES"))

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Select an example…")
        for preset in PRESETS:
            self.preset_combo.addItem(preset["label"])
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)
        lay.addWidget(self.preset_combo)
        return w

    def _advanced_section(self) -> QWidget:
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self.advanced_toggle = QToolButton()
        self.advanced_toggle.setObjectName("advanced_toggle")
        self.advanced_toggle.setText("▸  Advanced")
        self.advanced_toggle.setCheckable(True)
        self.advanced_toggle.setChecked(False)
        self.advanced_toggle.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.advanced_toggle.clicked.connect(self._toggle_advanced)

        self.advanced_panel = QWidget()
        adv_lay = QVBoxLayout(self.advanced_panel)
        adv_lay.setContentsMargins(8, 2, 0, 4)
        adv_lay.setSpacing(6)

        adv_lay.addLayout(self._adv_row("Tolerance",      "1e-8", "adv_tol"))
        adv_lay.addLayout(self._adv_row("Max iterations", "50",   "adv_maxiter"))
        adv_lay.addLayout(self._adv_row("x-axis  from",   "",     "adv_xmin", "auto"))
        adv_lay.addLayout(self._adv_row("x-axis  to",     "",     "adv_xmax", "auto"))

        self.advanced_panel.setVisible(False)

        lay.addWidget(self.advanced_toggle)
        lay.addWidget(self.advanced_panel)
        return container

    def _adv_row(self, label: str, default: str, attr: str, placeholder: str = "") -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {style.COLOR_TEXT_SECONDARY}; "
            f"font-family: '{style.FONT_UI}'; font-size: {style.SIZE_SMALL}pt;"
        )
        lbl.setFixedWidth(114)
        field = QLineEdit()
        field.setText(default)
        if placeholder:
            field.setPlaceholderText(placeholder)
        field.setFixedHeight(26)
        setattr(self, attr, field)
        row.addWidget(lbl)
        row.addWidget(field)
        return row

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_derivative_label(self, formula: str) -> None:
        self.deriv_label.setText(f"f′(x) = {formula}")

    def set_parse_error(self, message: str) -> None:
        if message:
            self.parse_error_label.setText(message)
            self.parse_error_label.setVisible(True)
            self.fx_input.setStyleSheet(
                f"border: 1px solid {style.COLOR_ERROR_FG};"
            )
            self.btn_run.setEnabled(False)
        else:
            self.parse_error_label.setVisible(False)
            self.fx_input.setStyleSheet("")
            self.btn_run.setEnabled(True)

    def set_step_state(self, current: int, total: int) -> None:
        """Update the step navigator label and enable/disable buttons."""
        self._step = current
        self._total_steps = total
        self.step_label.setText(f"Step {current} / {total}")
        self.btn_prev.setEnabled(current > 0)
        self.btn_next.setEnabled(current < total)

    def reset_navigator(self) -> None:
        self._step = 0
        self._total_steps = 0
        self.step_label.setText("Step — / —")
        self.btn_prev.setEnabled(False)
        self.btn_next.setEnabled(False)

    def get_tolerance(self) -> float:
        try:
            return float(self.adv_tol.text())
        except ValueError:
            return 1e-8

    def get_max_iter(self) -> int:
        try:
            return int(self.adv_maxiter.text())
        except ValueError:
            return 50

    def get_x_range(self) -> tuple[float, float] | None:
        try:
            return float(self.adv_xmin.text()), float(self.adv_xmax.text())
        except ValueError:
            return None

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_run(self) -> None:
        expr = self.fx_input.text().strip()
        try:
            x0 = float(self.x0_input.text())
        except ValueError:
            self.x0_input.setStyleSheet(f"border: 1px solid {style.COLOR_ERROR_FG};")
            return
        self.x0_input.setStyleSheet("")
        if expr:
            self.run_requested.emit(expr, x0)

    def _on_prev(self) -> None:
        if self._step > 0:
            new_step = self._step - 1
            self.set_step_state(new_step, self._total_steps)
            self.step_changed.emit(new_step)

    def _on_next(self) -> None:
        if self._step < self._total_steps:
            new_step = self._step + 1
            self.set_step_state(new_step, self._total_steps)
            self.step_changed.emit(new_step)

    def _toggle_advanced(self) -> None:
        visible = self.advanced_toggle.isChecked()
        self.advanced_panel.setVisible(visible)
        self.advanced_toggle.setText(
            "▾  Advanced" if visible else "▸  Advanced"
        )

    def _on_preset_selected(self, index: int) -> None:
        if index == 0:
            return
        preset = PRESETS[index - 1]
        self.fx_input.setText(preset["expr"])
        self.x0_input.setText(str(preset["x0"]))
        self.adv_tol.setText(str(preset["tol"]))
        self.adv_maxiter.setText(str(preset["max_iter"]))
        self.parse_error_label.setVisible(False)
        self.fx_input.setStyleSheet("")
        self.btn_run.setEnabled(True)
        self.deriv_label.setText("f′(x) = —")

    def _on_expr_edited(self) -> None:
        self.preset_combo.setCurrentIndex(0)
        self.deriv_label.setText("f′(x) = —")
