from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt

from app import style

_IDLE_HTML = (
    "<p>Enter a function and an initial guess above, "
    "then press <b>Run</b> to begin.</p>"
    f"<p style='color:{style.COLOR_TEXT_SECONDARY};'>"
    "Newton's method finds a root of f(x) by following "
    "the tangent line at each approximation down to the x-axis."
    "</p>"
)


class StatusPanel(QWidget):
    """Explanation panel and result badge.

    Public API:
        set_idle()
        set_explanation(html: str)
        set_badge(text: str, kind: str)   kind in {'success', 'warn', 'error'}
        clear_badge()
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("surface")
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            style.PANEL_PADDING_H, style.PANEL_PADDING_V,
            style.PANEL_PADDING_H, style.PANEL_PADDING_V,
        )
        outer.setSpacing(style.SECTION_GAP)

        section_lbl = QLabel("EXPLANATION")
        section_lbl.setStyleSheet(
            f"color: {style.COLOR_TEXT_SECONDARY}; "
            f"font-size: {style.SIZE_SECTION_LABEL}pt; "
            f"font-weight: 700; letter-spacing: 0.5px;"
        )
        outer.addWidget(section_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent;")

        self._explanation = QLabel()
        self._explanation.setWordWrap(True)
        self._explanation.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self._explanation.setTextFormat(Qt.TextFormat.RichText)
        self._explanation.setStyleSheet(
            f"font-size: {style.SIZE_BODY}pt; "
            f"color: {style.COLOR_TEXT_PRIMARY}; "
            "background: transparent;"
        )
        self._explanation.setContentsMargins(0, 0, 4, 0)
        scroll.setWidget(self._explanation)
        outer.addWidget(scroll, stretch=1)

        self._badge = QLabel()
        self._badge.setWordWrap(True)
        self._badge.setTextFormat(Qt.TextFormat.RichText)
        self._badge.setVisible(False)
        self._badge.setStyleSheet(
            f"border-radius: 4px; padding: 8px 10px; font-size: {style.SIZE_BODY}pt;"
        )
        outer.addWidget(self._badge)

        self.set_idle()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_idle(self) -> None:
        self._explanation.setText(_IDLE_HTML)
        self.clear_badge()

    def set_explanation(self, html: str) -> None:
        self._explanation.setText(html)

    def set_badge(self, text: str, kind: str) -> None:
        """Display a status badge.

        kind: 'success' | 'warn' | 'error'
        """
        palette = {
            "success": (style.COLOR_SUCCESS_BG, style.COLOR_SUCCESS_FG),
            "warn":    (style.COLOR_WARN_BG,    style.COLOR_WARN_FG),
            "error":   (style.COLOR_ERROR_BG,   style.COLOR_ERROR_FG),
        }
        bg, fg = palette.get(kind, (style.COLOR_SURFACE, style.COLOR_TEXT_PRIMARY))
        self._badge.setStyleSheet(
            f"background-color: {bg}; color: {fg}; "
            f"border-radius: 4px; padding: 8px 10px; "
            f"font-size: {style.SIZE_BODY}pt; font-weight: 600;"
        )
        self._badge.setText(text)
        self._badge.setVisible(True)

    def clear_badge(self) -> None:
        self._badge.setVisible(False)
