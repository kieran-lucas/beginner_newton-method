import os
import sys

# Must be set before any matplotlib import so the Qt backend is selected.
os.environ.setdefault("MPLBACKEND", "QtAgg")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app import style
from app.window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Newton's Method Explorer")
    app.setOrganizationName("beginner-newton-method")
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app.setStyleSheet(style.app_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
