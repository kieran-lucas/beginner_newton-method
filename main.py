import os
import sys

# Must be set before any matplotlib import so the Qt backend is selected.
os.environ.setdefault("MPLBACKEND", "QtAgg")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from app import style
from app.window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Newton's Method Explorer")
    app.setOrganizationName("beginner-newton-method")

    # Register Lexend fonts before anything uses QFont
    style.load_fonts()

    # Make Lexend the application-wide default font
    default_font = QFont(style.FONT_UI, style.SIZE_BODY)
    app.setFont(default_font)

    app.setStyleSheet(style.app_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
