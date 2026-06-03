from __future__ import annotations

import math
from typing import Callable

import numpy as np

_SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from app import style
from app.newton import IterationRecord, StopCode, tangent_line


class _MinimalToolbar(NavigationToolbar2QT):
    toolitems = [
        t for t in NavigationToolbar2QT.toolitems
        if t[0] in {"Home", "Pan", "Zoom"}
    ]


class PlotCanvas(QWidget):
    """Matplotlib canvas with Newton's method visualisation.

    Public API
    ----------
    reset()
        Idle state — no function plotted.
    new_run(f, steps, x_range)
        Called after a successful run.  Draws the curve and step 0.
    show_step(idx, show_all_tangents=False)
        Update the iteration overlay to display step idx.
    """

    _CURVE_POINTS = 600

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.fig    = Figure(facecolor=style.COLOR_BG)
        self.ax     = self.fig.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.toolbar = _MinimalToolbar(self.canvas, self)
        self.toolbar.setStyleSheet(
            "QToolButton { background: transparent; border: 1px solid #DDDDD8;"
            "  border-radius: 3px; margin: 1px; padding: 2px; }"
            "QToolButton:hover   { background: #F0F0EE; }"
            "QToolButton:checked { background: #EBF0FA;"
            "  border-color: #2B5EA7; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.canvas, stretch=1)
        layout.addWidget(self.toolbar)

        # Stored run data
        self._f:       Callable | None          = None
        self._steps:   list[IterationRecord]    = []
        self._x_range: tuple[float, float]      = (-5.0, 5.0)
        self._x_curve: np.ndarray | None        = None
        self._y_curve: np.ndarray | None        = None
        self._y_range: tuple[float, float]      = (-10.0, 10.0)

        self._draw_idle()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self) -> None:
        self._f      = None
        self._steps  = []
        self._x_curve = None
        self._y_curve = None
        self._draw_idle()

    def new_run(
        self,
        f:       Callable[[float], float],
        steps:   list[IterationRecord],
        x_range: tuple[float, float],
    ) -> None:
        self._f       = f
        self._steps   = steps
        self._x_range = x_range
        self._compute_curve()
        self.show_step(0)

    def show_step(self, idx: int, show_all_tangents: bool = False) -> None:
        if not self._steps or self._x_curve is None:
            return
        idx = max(0, min(idx, len(self._steps) - 1))
        self._redraw(idx, show_all_tangents)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _compute_curve(self) -> None:
        x0, x1 = self._x_range
        xs = np.linspace(x0, x1, self._CURVE_POINTS)
        ys = np.empty_like(xs)
        for i, xv in enumerate(xs):
            try:
                ys[i] = self._f(xv)
            except Exception:
                ys[i] = np.nan

        # Clamp extreme values for display
        clamp = style.PLOT_Y_CLAMP
        ys_disp = np.where(np.abs(ys) > clamp, np.nan, ys)

        self._x_curve = xs
        self._y_curve = ys_disp

        # Y range from valid values
        valid = ys_disp[np.isfinite(ys_disp)]
        if valid.size > 0:
            pad = max((valid.max() - valid.min()) * 0.12, 1.0)
            self._y_range = (float(valid.min()) - pad, float(valid.max()) + pad)
        else:
            self._y_range = (-10.0, 10.0)

    def _setup_axes(self) -> None:
        ax = self.ax
        ax.set_facecolor(style.COLOR_SURFACE)
        self.fig.set_facecolor(style.COLOR_BG)
        ax.axhline(0, color=style.COLOR_AXIS,
                   linewidth=style.PLOT_LINEWIDTH_AXIS, zorder=1)
        ax.axvline(0, color=style.COLOR_AXIS,
                   linewidth=style.PLOT_LINEWIDTH_AXIS, zorder=1)
        ax.grid(True, color=style.COLOR_GRID,
                linewidth=style.PLOT_LINEWIDTH_GRID, zorder=0)
        ax.set_xlabel("x",    color=style.COLOR_TEXT_SECONDARY, fontsize=9)
        ax.set_ylabel("f(x)", color=style.COLOR_TEXT_SECONDARY, fontsize=9)
        ax.tick_params(colors=style.COLOR_TEXT_SECONDARY, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(style.COLOR_BORDER)

    def _draw_idle(self) -> None:
        self.ax.clear()
        self._setup_axes()
        self.ax.text(
            0.5, 0.5,
            "Enter a function above and press Run",
            transform=self.ax.transAxes,
            ha="center", va="center",
            color=style.COLOR_TEXT_DISABLED,
            fontsize=10,
        )
        self.fig.tight_layout(pad=1.2)
        self.canvas.draw_idle()

    def _redraw(self, current_idx: int, show_all_tangents: bool) -> None:
        self.ax.clear()
        self._setup_axes()

        x0, x1 = self._x_range
        y0, y1 = self._y_range

        # ---- Function curve -------------------------------------------
        if self._x_curve is not None:
            self.ax.plot(
                self._x_curve, self._y_curve,
                color=style.COLOR_CURVE,
                linewidth=style.PLOT_LINEWIDTH_CURVE,
                zorder=3,
                label="f(x)",
            )

        # ---- Previous iteration tangents (faded) ----------------------
        if show_all_tangents:
            for i, s in enumerate(self._steps):
                if i >= current_idx:
                    break
                if s.x_next is None or s.df_xn == 0.0:
                    continue
                slope, intercept = tangent_line(s.x_n, s.f_xn, s.df_xn)
                t_xs = np.array([x0, x1])
                t_ys = slope * t_xs + intercept
                self.ax.plot(
                    t_xs, t_ys,
                    color=style.COLOR_TANGENT,
                    alpha=style.COLOR_TANGENT_ALPHA,
                    linewidth=1.0,
                    zorder=2,
                )

        # ---- Previous x_n markers (small, subdued) --------------------
        for i, s in enumerate(self._steps):
            if i >= current_idx:
                break
            if not (math.isfinite(s.x_n) and math.isfinite(s.f_xn)):
                continue
            self.ax.plot(
                s.x_n, s.f_xn,
                "o",
                color=style.COLOR_TEXT_SECONDARY,
                markersize=4,
                zorder=4,
                alpha=0.5,
            )

        # ---- Current step ---------------------------------------------
        step = self._steps[current_idx]

        # Vertical drop line from curve to x-axis
        if step.f_xn is not None and not (step.f_xn != step.f_xn):  # not NaN
            self.ax.plot(
                [step.x_n, step.x_n], [0.0, step.f_xn],
                color=style.COLOR_TEXT_SECONDARY,
                linewidth=0.8, linestyle="--", alpha=0.5, zorder=2,
            )

        # Current tangent line (full opacity)
        if step.x_next is not None and step.df_xn != 0.0:
            slope, intercept = tangent_line(step.x_n, step.f_xn, step.df_xn)
            t_xs = np.array([x0, x1])
            t_ys = slope * t_xs + intercept
            self.ax.plot(
                t_xs, t_ys,
                color=style.COLOR_TANGENT,
                linewidth=style.PLOT_LINEWIDTH_TANGENT,
                zorder=4,
                linestyle="--",
                label="tangent",
            )

            # x_{n+1} marker on x-axis
            self.ax.plot(
                step.x_next, 0.0,
                "o",
                color=style.COLOR_TANGENT,
                markerfacecolor="white",
                markeredgewidth=1.5,
                markersize=7,
                zorder=5,
            )
            self.ax.annotate(
                f"x{current_idx + 1}".translate(_SUB),
                (step.x_next, 0.0),
                xytext=(0, -12), textcoords="offset points",
                ha="center", va="top",
                fontsize=8,
                color=style.COLOR_TANGENT,
            )

        # Current point (x_n, f(x_n))
        self.ax.plot(
            step.x_n, step.f_xn,
            "o",
            color=style.COLOR_POINT,
            markersize=style.PLOT_POINT_RADIUS + 1,
            zorder=6,
        )

        # ---- Root marker (converged) -----------------------------------
        sc = step.status
        if sc in (StopCode.CONVERGED_RESIDUAL.value,
                  StopCode.CONVERGED_STEP.value):
            root_x = step.x_n if sc == StopCode.CONVERGED_RESIDUAL.value \
                     else step.x_next
            if root_x is not None:
                self.ax.plot(
                    root_x, 0.0,
                    "*",
                    color=style.COLOR_ROOT,
                    markersize=12,
                    zorder=7,
                    label="root",
                )
                self.ax.annotate(
                    f"root ≈ {root_x:.5g}",
                    (root_x, 0.0),
                    xytext=(4, 8), textcoords="offset points",
                    fontsize=8, color=style.COLOR_ROOT,
                )

        # ---- Step annotation in corner --------------------------------
        total = len(self._steps)
        self.ax.text(
            0.02, 0.98,
            f"Step {current_idx} / {total - 1}",
            transform=self.ax.transAxes,
            ha="left", va="top",
            fontsize=8,
            color=style.COLOR_TEXT_SECONDARY,
        )

        # ---- Axis limits -----------------------------------------------
        self.ax.set_xlim(x0, x1)
        self.ax.set_ylim(y0, y1)

        self.fig.tight_layout(pad=1.0)
        self.canvas.draw_idle()
