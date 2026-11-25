"""Cached, translucent stone pixmaps for board hover previews."""

from functools import lru_cache
from pathlib import Path

from PySide6 import QtCore, QtGui


_STONE_FILES = {
    1: "black_stone.svg",
    2: "white_stone.svg",
}


@lru_cache(maxsize=2)
def stone_pixmap(color: int) -> QtGui.QPixmap:
    """Load and cache the solid stone image for a board color."""
    try:
        filename = _STONE_FILES[color]
    except KeyError as error:
        raise ValueError(f"Unsupported stone color: {color}") from error
    image_path = Path(__file__).resolve().parent / "assets" / filename
    pixmap = QtGui.QPixmap(str(image_path))
    if pixmap.isNull():
        raise FileNotFoundError(f"Could not load stone image: {image_path}")
    return pixmap


@lru_cache(maxsize=2)
def stone_preview(color: int) -> QtGui.QPixmap:
    """Return a cached semi-transparent stone pixmap for a board color."""
    source = stone_pixmap(color)
    preview = QtGui.QPixmap(source.size())
    preview.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(preview)
    painter.setOpacity(0.42)
    painter.drawPixmap(0, 0, source)
    painter.end()
    return preview
