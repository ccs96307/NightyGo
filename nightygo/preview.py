"""Cached stone images and translucent hover previews."""

from __future__ import annotations

import random
from functools import lru_cache
from pathlib import Path

from PySide6 import QtCore, QtGui

from nightygo.materials import STONE_MATERIALS


_STONE_FILES = {
    1: "black_stone.svg",
    2: "white_stone.svg",
}


@lru_cache(maxsize=6)
def stone_pixmap(color: int, material: str = "classic") -> QtGui.QPixmap:
    """Load or generate and cache a stone image."""
    if color not in _STONE_FILES:
        raise ValueError(f"Unsupported stone color: {color}")
    if material not in STONE_MATERIALS.values():
        raise ValueError(f"Unsupported stone material: {material}")
    if material != "classic":
        return _textured_stone(color, material)
    image_path = Path(__file__).resolve().parent / "assets" / _STONE_FILES[color]
    pixmap = QtGui.QPixmap(str(image_path))
    if pixmap.isNull():
        raise FileNotFoundError(f"Could not load stone image: {image_path}")
    return pixmap


@lru_cache(maxsize=6)
def stone_preview(color: int, material: str = "classic") -> QtGui.QPixmap:
    """Return a cached semi-transparent stone preview."""
    source = stone_pixmap(color, material)
    preview = QtGui.QPixmap(source.size())
    preview.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(preview)
    painter.setOpacity(0.42)
    painter.drawPixmap(0, 0, source)
    painter.end()
    return preview


def _textured_stone(color: int, material: str) -> QtGui.QPixmap:
    image = QtGui.QPixmap(250, 250)
    image.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(image)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    clip = QtGui.QPainterPath()
    clip.addEllipse(QtCore.QRectF(9, 9, 232, 232))
    painter.setClipPath(clip)

    if material == "starfield":
        colors = (
            ("#506ab9", "#191634", "#070916")
            if color == 1
            else ("#ffffff", "#d5e1ff", "#8995b8")
        )
        seed = 109 if color == 1 else 211
    else:
        colors = (
            ("#7b8792", "#313b48", "#171d27")
            if color == 1
            else ("#fffdf4", "#d9d8d1", "#9c9e9f")
        )
        seed = 317 if color == 1 else 419

    gradient = QtGui.QRadialGradient(80, 66, 225)
    gradient.setColorAt(0, QtGui.QColor(colors[0]))
    gradient.setColorAt(0.55, QtGui.QColor(colors[1]))
    gradient.setColorAt(1, QtGui.QColor(colors[2]))
    painter.fillRect(image.rect(), gradient)

    if material == "starfield":
        _draw_stars(painter, seed)
    else:
        _draw_moon_craters(painter, color, seed)
    painter.end()

    painter = QtGui.QPainter(image)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
    painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 75), 2.0))
    painter.drawEllipse(QtCore.QRectF(10, 10, 230, 230))
    highlight = QtGui.QRadialGradient(68, 57, 100)
    highlight.setColorAt(0, QtGui.QColor(255, 255, 255, 65))
    highlight.setColorAt(1, QtGui.QColor(255, 255, 255, 0))
    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    painter.setBrush(highlight)
    painter.drawEllipse(QtCore.QRectF(20, 18, 150, 140))
    painter.end()
    return image


def _draw_stars(painter: QtGui.QPainter, seed: int) -> None:
    rng = random.Random(seed)
    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    for _ in range(72):
        x, y = rng.uniform(10, 240), rng.uniform(10, 240)
        radius = rng.choices((0.6, 1.0, 1.5, 2.0), (46, 20, 5, 1))[0]
        painter.setBrush(QtGui.QColor(rng.choice(("#ffffff", "#b5d8ff", "#d9bdff"))))
        painter.drawEllipse(QtCore.QPointF(x, y), radius, radius)
    painter.setPen(QtGui.QPen(QtGui.QColor(226, 234, 255, 170), 1.1))
    for x, y in ((74, 149), (177, 82), (156, 191)):
        painter.drawLine(QtCore.QPointF(x - 4, y), QtCore.QPointF(x + 4, y))
        painter.drawLine(QtCore.QPointF(x, y - 4), QtCore.QPointF(x, y + 4))


def _draw_moon_craters(painter: QtGui.QPainter, color: int, seed: int) -> None:
    rng = random.Random(seed)
    shade = QtGui.QColor(20, 28, 38, 24) if color == 1 else QtGui.QColor(78, 85, 93, 34)
    painter.setPen(QtGui.QPen(shade, 1.2))
    painter.setBrush(QtGui.QColor(shade.red(), shade.green(), shade.blue(), 12))
    for _ in range(12):
        x, y = rng.uniform(35, 215), rng.uniform(35, 215)
        radius = rng.uniform(5, 15)
        painter.drawEllipse(QtCore.QPointF(x, y), radius * 1.35, radius)
