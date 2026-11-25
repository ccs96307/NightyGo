"""Procedurally rendered board and stone materials."""

from __future__ import annotations

import math
import random
from functools import lru_cache

from PySide6 import QtCore, QtGui

BOARD_MATERIALS = {
    "Classic wood": "wood",
    "Starfield": "starfield",
    "Night sky": "night_sky",
}

STONE_MATERIALS = {
    "Traditional": "classic",
    "Starfield": "starfield",
    "Moonstone": "moonstone",
}


@lru_cache(maxsize=3)
def board_texture(material: str) -> QtGui.QImage:
    """Build and cache a 512px square board surface texture."""
    image = QtGui.QImage(512, 512, QtGui.QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(image)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
    if material == "wood":
        _paint_wood(painter)
    elif material == "starfield":
        _paint_starfield(painter)
    else:
        _paint_night_sky(painter)
    painter.end()
    return image


def _paint_wood(painter: QtGui.QPainter) -> None:
    gradient = QtGui.QLinearGradient(0, 0, 512, 512)
    gradient.setColorAt(0, QtGui.QColor("#f0cf82"))
    gradient.setColorAt(0.45, QtGui.QColor("#d7ad68"))
    gradient.setColorAt(1, QtGui.QColor("#c6964e"))
    painter.fillRect(0, 0, 512, 512, gradient)
    rng = random.Random(1947)
    for _ in range(90):
        y = rng.uniform(-20, 532)
        amplitude = rng.uniform(1, 12)
        phase = rng.uniform(0, 512)
        path = QtGui.QPainterPath(QtCore.QPointF(-8, y))
        path.cubicTo(
            120,
            y + amplitude * math.sin(phase),
            320,
            y + amplitude * math.cos(phase * 0.7),
            520,
            y + rng.uniform(-3, 3),
        )
        color = QtGui.QColor("#7b4d24")
        color.setAlpha(rng.randint(7, 24))
        painter.setPen(QtGui.QPen(color, rng.uniform(0.4, 2.4)))
        painter.drawPath(path)
    for x, y in ((126, 172), (383, 376)):
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        for radius in (7, 13, 20):
            color = QtGui.QColor("#8c572b")
            color.setAlpha(22)
            painter.setPen(QtGui.QPen(color, 1.1))
            painter.drawEllipse(QtCore.QPointF(x, y), radius * 1.6, radius * 0.55)


def _paint_starfield(painter: QtGui.QPainter) -> None:
    painter.fillRect(0, 0, 512, 512, QtGui.QColor("#080d22"))
    _paint_nebula(painter, ((120, 175, "#442b88"), (360, 345, "#154b72")))
    rng = random.Random(951)
    for _ in range(620):
        x, y = rng.uniform(0, 512), rng.uniform(0, 512)
        radius = rng.choices((0.6, 1.0, 1.6, 2.2), (60, 28, 10, 2))[0]
        color = rng.choice(("#dce8ff", "#a9c8ff", "#f3d8a5", "#e6c5ff"))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(color))
        painter.drawEllipse(QtCore.QPointF(x, y), radius, radius)


def _paint_night_sky(painter: QtGui.QPainter) -> None:
    gradient = QtGui.QLinearGradient(0, 0, 0, 512)
    gradient.setColorAt(0, QtGui.QColor("#101b3b"))
    gradient.setColorAt(0.53, QtGui.QColor("#263b63"))
    gradient.setColorAt(1, QtGui.QColor("#111a35"))
    painter.fillRect(0, 0, 512, 512, gradient)
    _paint_nebula(painter, ((155, 328, "#376c83"), (374, 245, "#6a477c")))
    rng = random.Random(461)
    for _ in range(280):
        x, y = rng.uniform(0, 512), rng.uniform(0, 512)
        radius = rng.uniform(0.5, 1.5)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor("#d7e6ff"))
        painter.drawEllipse(QtCore.QPointF(x, y), radius, radius)
    painter.setPen(QtGui.QPen(QtGui.QColor(245, 227, 178, 70), 2))
    painter.setBrush(QtGui.QColor(245, 227, 178, 25))
    painter.drawEllipse(QtCore.QPointF(393, 104), 35, 35)


def _paint_nebula(painter: QtGui.QPainter, clouds) -> None:
    painter.save()
    for x, y, color in clouds:
        gradient = QtGui.QRadialGradient(x, y, 170)
        center = QtGui.QColor(color)
        center.setAlpha(95)
        edge = QtGui.QColor(color)
        edge.setAlpha(0)
        gradient.setColorAt(0, center)
        gradient.setColorAt(1, edge)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(QtCore.QPointF(x, y), 170, 170)
    painter.restore()
