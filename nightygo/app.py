"""Application entry point."""

import sys

from PySide6 import QtWidgets

from nightygo.ui.main_window import MainWindow


def main() -> int:
    """Run NightyGo and return the Qt event-loop exit code."""
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("NightyGo")
    window = MainWindow()
    window.show()
    return app.exec()
