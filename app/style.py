from __future__ import annotations
from pathlib import Path

# --- Color palette ---
COLOR_BG             = "#F5F5F3"
COLOR_SURFACE        = "#FFFFFF"
COLOR_BORDER         = "#E2E2DC"
COLOR_TEXT_PRIMARY   = "#18181B"
COLOR_TEXT_SECONDARY = "#71717A"
COLOR_TEXT_DISABLED  = "#B8B8B4"
COLOR_ACCENT         = "#2B5EA7"
COLOR_ACCENT_HOVER   = "#1E4585"
COLOR_ACCENT_PRESSED = "#163C6E"
COLOR_ACCENT_TEXT    = "#FFFFFF"
COLOR_ACCENT_LIGHT   = "#EEF3FB"

# Plot-specific (Matplotlib)
COLOR_CURVE          = "#1A3C6E"
COLOR_TANGENT        = "#D45F2A"
COLOR_TANGENT_ALPHA  = 0.18
COLOR_POINT          = "#18181B"
COLOR_ROOT           = "#15803D"
COLOR_GRID           = "#EBEBEB"
COLOR_AXIS           = "#9CA3AF"

# Semantic badge colors
COLOR_SUCCESS_BG     = "#DCFCE7"
COLOR_SUCCESS_FG     = "#166534"
COLOR_WARN_BG        = "#FEF9C3"
COLOR_WARN_FG        = "#854D0E"
COLOR_ERROR_BG       = "#FEE2E2"
COLOR_ERROR_FG       = "#991B1B"
COLOR_ROW_SELECTED   = "#EEF3FB"

# --- Layout dimensions (px) ---
SIDEBAR_DEFAULT_WIDTH = 330
SIDEBAR_MIN_WIDTH     = 270
WINDOW_MIN_W          = 1020
WINDOW_MIN_H          = 680
WINDOW_DEFAULT_W      = 1240
WINDOW_DEFAULT_H      = 800
BUTTON_H              = 34
TABLE_ROW_H           = 26
PANEL_PADDING_H       = 18
PANEL_PADDING_V       = 16
SECTION_GAP           = 12

# --- Font families ---
FONT_UI   = "Lexend"
FONT_MONO = "Consolas"

# --- Font sizes (pt) ---
SIZE_INPUT         = 13
SIZE_FORMULA       = 11
SIZE_TABLE         = 9
SIZE_BODY          = 10
SIZE_SMALL         = 9
SIZE_SECTION_LABEL = 8

# --- Matplotlib parameters ---
PLOT_LINEWIDTH_CURVE   = 2.0
PLOT_LINEWIDTH_TANGENT = 1.6
PLOT_LINEWIDTH_AXIS    = 0.8
PLOT_LINEWIDTH_GRID    = 0.5
PLOT_POINT_RADIUS      = 5
PLOT_Y_CLAMP           = 30.0


def load_fonts() -> None:
    """Register all Lexend TTF weights with Qt and matplotlib."""
    _lexend = Path(__file__).parent.parent / "lexend"

    from PyQt6.QtGui import QFontDatabase
    for ttf in sorted(_lexend.glob("*.ttf")):
        QFontDatabase.addApplicationFont(str(ttf))

    try:
        from matplotlib import font_manager as _fm
        import matplotlib as _mpl
        for ttf in sorted(_lexend.glob("*.ttf")):
            _fm.fontManager.addfont(str(ttf.resolve()))
        _mpl.rcParams.update({
            "font.family":     "Lexend",
            "font.size":       9,
            "axes.titlesize":  9,
            "axes.labelsize":  9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
        })
    except Exception:
        pass


def app_stylesheet() -> str:
    return f"""
    /* ── Base ──────────────────────────────────────────────────────────── */
    QMainWindow, QWidget {{
        background-color: {COLOR_BG};
        color: {COLOR_TEXT_PRIMARY};
        font-family: "{FONT_UI}";
        font-size: {SIZE_BODY}pt;
    }}

    QWidget#surface {{
        background-color: {COLOR_SURFACE};
    }}

    /* ── Splitter ───────────────────────────────────────────────────────── */
    QSplitter::handle:horizontal {{
        background-color: {COLOR_BORDER};
        width: 1px;
    }}
    QSplitter::handle:vertical {{
        background-color: {COLOR_BORDER};
        height: 1px;
    }}

    /* ── QLineEdit ──────────────────────────────────────────────────────── */
    QLineEdit {{
        background-color: {COLOR_SURFACE};
        border: 1.5px solid {COLOR_BORDER};
        border-radius: 5px;
        padding: 5px 10px;
        color: {COLOR_TEXT_PRIMARY};
        font-family: "{FONT_UI}";
        font-size: {SIZE_BODY}pt;
        selection-background-color: {COLOR_ACCENT};
        selection-color: {COLOR_ACCENT_TEXT};
    }}
    QLineEdit:focus {{
        border-color: {COLOR_ACCENT};
        background-color: {COLOR_SURFACE};
    }}
    QLineEdit:disabled {{
        background-color: {COLOR_BG};
        color: {COLOR_TEXT_DISABLED};
        border-color: {COLOR_BORDER};
    }}

    /* ── QPushButton ────────────────────────────────────────────────────── */
    QPushButton {{
        background-color: {COLOR_SURFACE};
        border: 1.5px solid {COLOR_BORDER};
        border-radius: 5px;
        padding: 0px 14px;
        height: {BUTTON_H}px;
        color: {COLOR_TEXT_PRIMARY};
        font-family: "{FONT_UI}";
        font-size: {SIZE_BODY}pt;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: #F0F0EE;
        border-color: #C4C4C0;
    }}
    QPushButton:pressed {{
        background-color: #E8E8E5;
        border-color: #B8B8B4;
    }}
    QPushButton:disabled {{
        color: {COLOR_TEXT_DISABLED};
        border-color: {COLOR_BORDER};
        background-color: {COLOR_BG};
    }}
    QPushButton#btn_run {{
        background-color: {COLOR_ACCENT};
        color: {COLOR_ACCENT_TEXT};
        border: none;
        font-weight: 600;
    }}
    QPushButton#btn_run:hover {{
        background-color: {COLOR_ACCENT_HOVER};
    }}
    QPushButton#btn_run:pressed {{
        background-color: {COLOR_ACCENT_PRESSED};
    }}
    QPushButton#btn_run:disabled {{
        background-color: {COLOR_TEXT_DISABLED};
        color: {COLOR_SURFACE};
        border: none;
    }}

    /* ── QComboBox ──────────────────────────────────────────────────────── */
    QComboBox {{
        background-color: {COLOR_SURFACE};
        border: 1.5px solid {COLOR_BORDER};
        border-radius: 5px;
        padding: 0px 10px;
        height: {BUTTON_H}px;
        color: {COLOR_TEXT_PRIMARY};
        font-family: "{FONT_UI}";
        font-size: {SIZE_BODY}pt;
    }}
    QComboBox:focus {{
        border-color: {COLOR_ACCENT};
    }}
    QComboBox:hover {{
        border-color: #C4C4C0;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 26px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLOR_SURFACE};
        border: 1.5px solid {COLOR_BORDER};
        selection-background-color: {COLOR_ROW_SELECTED};
        selection-color: {COLOR_TEXT_PRIMARY};
        outline: none;
        padding: 2px;
    }}
    QComboBox QAbstractItemView::item {{
        padding: 5px 10px;
        min-height: 26px;
        font-family: "{FONT_UI}";
    }}

    /* ── QTableWidget ───────────────────────────────────────────────────── */
    QTableWidget {{
        background-color: {COLOR_SURFACE};
        gridline-color: {COLOR_BORDER};
        border: none;
        border-top: 1px solid {COLOR_BORDER};
        selection-background-color: {COLOR_ROW_SELECTED};
        selection-color: {COLOR_TEXT_PRIMARY};
        outline: none;
        font-family: "{FONT_MONO}";
        font-size: {SIZE_TABLE}pt;
    }}
    QTableWidget::item {{
        padding: 0px 8px;
        border: none;
    }}
    QTableWidget::item:selected {{
        background-color: {COLOR_ROW_SELECTED};
        color: {COLOR_TEXT_PRIMARY};
    }}
    QHeaderView {{
        background-color: {COLOR_BG};
    }}
    QHeaderView::section {{
        background-color: {COLOR_BG};
        color: {COLOR_TEXT_SECONDARY};
        border: none;
        border-bottom: 1.5px solid {COLOR_BORDER};
        border-right: 1px solid {COLOR_BORDER};
        padding: 5px 8px;
        font-family: "{FONT_UI}";
        font-weight: 600;
        font-size: {SIZE_SMALL}pt;
    }}
    QHeaderView::section:last-child {{
        border-right: none;
    }}

    /* ── QScrollBar ─────────────────────────────────────────────────────── */
    QScrollBar:vertical {{
        background: transparent;
        width: 7px;
        border: none;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: #CECEC9;
        border-radius: 3px;
        min-height: 28px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #ADADAA;
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 7px;
        border: none;
        margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: #CECEC9;
        border-radius: 3px;
        min-width: 28px;
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ── Advanced toggle ────────────────────────────────────────────────── */
    QToolButton#advanced_toggle {{
        background: transparent;
        border: none;
        color: {COLOR_TEXT_SECONDARY};
        font-family: "{FONT_UI}";
        font-size: {SIZE_SECTION_LABEL}pt;
        font-weight: 600;
        text-align: left;
        padding: 0px;
    }}
    QToolButton#advanced_toggle:hover {{
        color: {COLOR_TEXT_PRIMARY};
    }}
    QToolButton#advanced_toggle:checked {{
        color: {COLOR_ACCENT};
    }}
    """
