# Visual constants for Newton's Method Explorer.
# Edit here — values cascade to every widget via app_stylesheet().

# --- Color tokens ---
COLOR_BG = "#F7F7F5"
COLOR_SURFACE = "#FFFFFF"
COLOR_BORDER = "#DDDDD8"
COLOR_TEXT_PRIMARY = "#1A1A1A"
COLOR_TEXT_SECONDARY = "#6B6B6B"
COLOR_TEXT_DISABLED = "#B0B0B0"
COLOR_ACCENT = "#2B5EA7"
COLOR_ACCENT_HOVER = "#1E4585"
COLOR_ACCENT_TEXT = "#FFFFFF"

# Plot-specific colors (used in Matplotlib, not Qt stylesheets)
COLOR_CURVE = "#1A3C6E"
COLOR_TANGENT = "#D45F2A"
COLOR_TANGENT_ALPHA = 0.15       # opacity for faded previous tangents
COLOR_POINT = "#1A1A1A"
COLOR_ROOT = "#2D7A2D"
COLOR_GRID = "#EBEBEB"
COLOR_AXIS = "#9B9B9B"

# Badge colors
COLOR_SUCCESS_BG = "#E8F5E9"
COLOR_SUCCESS_FG = "#1B5E20"
COLOR_WARN_BG = "#FFF8E1"
COLOR_WARN_FG = "#795548"
COLOR_ERROR_BG = "#FFEBEE"
COLOR_ERROR_FG = "#B71C1C"
COLOR_ROW_SELECTED = "#EBF0FA"

# --- Layout dimensions (px) ---
SIDEBAR_DEFAULT_WIDTH = 320
SIDEBAR_MIN_WIDTH = 260
WINDOW_MIN_W = 1000
WINDOW_MIN_H = 680
WINDOW_DEFAULT_W = 1200
WINDOW_DEFAULT_H = 780
BUTTON_H = 32
TABLE_ROW_H = 24
PANEL_PADDING_H = 16
PANEL_PADDING_V = 14
SECTION_GAP = 10

# --- Font sizes (pt) ---
SIZE_INPUT = 13
SIZE_FORMULA = 11
SIZE_TABLE = 10
SIZE_BODY = 10
SIZE_SMALL = 9
SIZE_SECTION_LABEL = 9

# --- Matplotlib plot parameters ---
PLOT_LINEWIDTH_CURVE = 2.0
PLOT_LINEWIDTH_TANGENT = 1.5
PLOT_LINEWIDTH_AXIS = 0.8
PLOT_LINEWIDTH_GRID = 0.6
PLOT_POINT_RADIUS = 5
PLOT_Y_CLAMP = 30.0


def app_stylesheet() -> str:
    """Return the complete Qt stylesheet for the application."""
    return f"""
    QMainWindow, QWidget {{
        background-color: {COLOR_BG};
        color: {COLOR_TEXT_PRIMARY};
        font-size: 10pt;
    }}

    QSplitter::handle:horizontal {{
        background-color: {COLOR_BORDER};
        width: 1px;
    }}
    QSplitter::handle:vertical {{
        background-color: {COLOR_BORDER};
        height: 1px;
    }}

    QLineEdit {{
        background-color: {COLOR_SURFACE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 3px;
        padding: 4px 8px;
        color: {COLOR_TEXT_PRIMARY};
        selection-background-color: {COLOR_ACCENT};
    }}
    QLineEdit:focus {{
        border-color: {COLOR_ACCENT};
        outline: none;
    }}
    QLineEdit:disabled {{
        background-color: {COLOR_BG};
        color: {COLOR_TEXT_DISABLED};
        border-color: {COLOR_BORDER};
    }}

    QPushButton {{
        background-color: {COLOR_SURFACE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 3px;
        padding: 0px 14px;
        height: {BUTTON_H}px;
        color: {COLOR_TEXT_PRIMARY};
    }}
    QPushButton:hover {{
        background-color: #F0F0EE;
        border-color: #C0C0BC;
    }}
    QPushButton:pressed {{
        background-color: #E8E8E5;
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
        background-color: #163C6E;
    }}
    QPushButton#btn_run:disabled {{
        background-color: {COLOR_TEXT_DISABLED};
        color: {COLOR_SURFACE};
        border: none;
    }}

    QComboBox {{
        background-color: {COLOR_SURFACE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 3px;
        padding: 0px 8px;
        height: {BUTTON_H}px;
        color: {COLOR_TEXT_PRIMARY};
    }}
    QComboBox:focus {{
        border-color: {COLOR_ACCENT};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLOR_SURFACE};
        border: 1px solid {COLOR_BORDER};
        selection-background-color: {COLOR_ROW_SELECTED};
        selection-color: {COLOR_TEXT_PRIMARY};
        outline: none;
    }}

    QTableWidget {{
        background-color: {COLOR_SURFACE};
        gridline-color: {COLOR_BORDER};
        border: none;
        selection-background-color: {COLOR_ROW_SELECTED};
        selection-color: {COLOR_TEXT_PRIMARY};
        outline: none;
    }}
    QTableWidget::item {{
        padding: 0px 8px;
        border: none;
    }}
    QHeaderView::section {{
        background-color: {COLOR_BG};
        color: {COLOR_TEXT_SECONDARY};
        border: none;
        border-bottom: 1px solid {COLOR_BORDER};
        border-right: 1px solid {COLOR_BORDER};
        padding: 4px 8px;
        font-weight: 600;
        font-size: {SIZE_SMALL}pt;
        font-family: sans-serif;
    }}

    QScrollBar:vertical {{
        background: {COLOR_BG};
        width: 10px;
        border: none;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {COLOR_BORDER};
        border-radius: 5px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #C8C8C4;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: {COLOR_BG};
        height: 10px;
        border: none;
        margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLOR_BORDER};
        border-radius: 5px;
        min-width: 24px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    QToolButton#advanced_toggle {{
        background: transparent;
        border: none;
        color: {COLOR_TEXT_SECONDARY};
        font-size: {SIZE_SECTION_LABEL}pt;
        font-weight: 700;
        text-align: left;
        padding: 0px;
    }}
    QToolButton#advanced_toggle:hover {{
        color: {COLOR_TEXT_PRIMARY};
    }}
    """
