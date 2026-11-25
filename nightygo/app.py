"""Application entry point."""

import logging
import os
import sys

from PySide6 import QtCore, QtWidgets

from nightygo.ui.main_window import MainWindow


logger = logging.getLogger("nightygo")


def configure_logging() -> None:
    """Configure readable application logs and silence known Qt chatter."""
    level_name = os.environ.get("NIGHTYGO_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    QtCore.QLoggingCategory.setFilterRules(
        "qt.qpa.wayland.textinput=false\n"
        "qt.multimedia.ffmpeg.info=false"
    )


def main() -> int:
    """Run NightyGo and return the Qt event-loop exit code."""
    configure_logging()
    logger.info("Starting NightyGo")
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("NightyGo")
    try:
        window = MainWindow()
    except Exception:
        logger.exception("Could not initialize the main window")
        raise
    window.show()
    exit_code = app.exec()
    logger.info("NightyGo exited with status %d", exit_code)
    return exit_code
