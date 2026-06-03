from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from app import style


_COLUMNS: list[tuple[str, int, Qt.AlignmentFlag]] = [
    ("n",       40,  Qt.AlignmentFlag.AlignCenter),
    ("xₙ",     120,  Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter),
    ("f(xₙ)",  110,  Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter),
    ("f′(xₙ)", 110,  Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter),
    ("xₙ₊₁",  120,  Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter),
    ("|step|",  100,  Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter),
    ("status",  90,  Qt.AlignmentFlag.AlignCenter),
]

_STATUS_COLORS: dict[str, tuple[str, str]] = {
    "CONVERGED_RESIDUAL":     (style.COLOR_SUCCESS_BG, style.COLOR_SUCCESS_FG),
    "CONVERGED_STEP":         (style.COLOR_SUCCESS_BG, style.COLOR_SUCCESS_FG),
    "MAX_ITERATIONS_REACHED": (style.COLOR_WARN_BG,    style.COLOR_WARN_FG),
    "ZERO_DERIVATIVE":        (style.COLOR_ERROR_BG,   style.COLOR_ERROR_FG),
    "NON_FINITE_VALUE":       (style.COLOR_ERROR_BG,   style.COLOR_ERROR_FG),
    "DOMAIN_ERROR":           (style.COLOR_ERROR_BG,   style.COLOR_ERROR_FG),
    "DIVERGENCE_SUSPECTED":   (style.COLOR_ERROR_BG,   style.COLOR_ERROR_FG),
}

_STATUS_LABELS: dict[str, str] = {
    "running":                "—",
    "CONVERGED_RESIDUAL":     "converged",
    "CONVERGED_STEP":         "converged",
    "MAX_ITERATIONS_REACHED": "max iter",
    "ZERO_DERIVATIVE":        "f′ = 0",
    "NON_FINITE_VALUE":       "non-finite",
    "DOMAIN_ERROR":           "domain err",
    "DIVERGENCE_SUSPECTED":   "diverging",
}


class TablePanel(QWidget):
    """Iteration data table.

    Emits step_selected(int) when the user clicks a row.
    Populated in Stage 5 via load_steps(steps).
    """

    step_selected = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._loading = False
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(len(_COLUMNS))
        self.table.setHorizontalHeaderLabels([c[0] for c in _COLUMNS])
        self.table.setRowCount(0)
        self.table.setShowGrid(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        for i, (_, width, _) in enumerate(_COLUMNS):
            self.table.setColumnWidth(i, width)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setDefaultSectionSize(style.TABLE_ROW_H)

        mono = QFont("Consolas")
        mono.setStyleHint(QFont.StyleHint.TypeWriter)
        mono.setPointSize(style.SIZE_TABLE)
        self.table.setFont(mono)

        header_font = QFont(style.FONT_UI)
        header_font.setPointSize(style.SIZE_SMALL)
        header_font.setWeight(QFont.Weight.DemiBold)
        self.table.horizontalHeader().setFont(header_font)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.table)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_steps(self, steps: list[dict]) -> None:
        """Populate the table from a list of step records.

        Each record must have: n, x_n, f_xn, df_xn, x_next, step_size, status.
        """
        self._loading = True
        self.table.setRowCount(0)
        self.table.setRowCount(len(steps))

        for row, step in enumerate(steps):
            self._set_cell(row, 0, str(step["n"]), _COLUMNS[0][2])
            self._set_cell(row, 1, f"{step['x_n']:.8g}", _COLUMNS[1][2])
            self._set_cell(row, 2, f"{step['f_xn']:.6g}", _COLUMNS[2][2])
            self._set_cell(row, 3, f"{step['df_xn']:.6g}", _COLUMNS[3][2])

            x_next = step.get("x_next")
            self._set_cell(row, 4, f"{x_next:.8g}" if x_next is not None else "—", _COLUMNS[4][2])

            step_size = step.get("step_size")
            self._set_cell(
                row, 5,
                f"{step_size:.3e}" if step_size is not None else "—",
                _COLUMNS[5][2],
            )

            status = step.get("status", "running")
            label = _STATUS_LABELS.get(status, status.replace("_", " "))
            status_item = QTableWidgetItem(label)
            status_item.setTextAlignment(int(_COLUMNS[6][2]))
            if status in _STATUS_COLORS:
                bg, fg = _STATUS_COLORS[status]
                status_item.setBackground(QColor(bg))
                status_item.setForeground(QColor(fg))
            self.table.setItem(row, 6, status_item)

            self.table.setRowHeight(row, style.TABLE_ROW_H)

        self._loading = False

    def select_row(self, index: int) -> None:
        """Select a row programmatically without emitting step_selected."""
        self._loading = True
        self.table.selectRow(index)
        self.table.scrollToItem(self.table.item(index, 0))
        self._loading = False

    def clear(self) -> None:
        self.table.setRowCount(0)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _set_cell(self, row: int, col: int, text: str, alignment: Qt.AlignmentFlag) -> None:
        item = QTableWidgetItem(text)
        item.setTextAlignment(int(alignment))
        self.table.setItem(row, col, item)

    def _on_selection_changed(self) -> None:
        if self._loading:
            return
        selected = self.table.selectedItems()
        if selected:
            self.step_selected.emit(self.table.currentRow())
