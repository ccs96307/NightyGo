"""Compact, high-contrast win-rate history graph."""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets
from nightygo.i18n import translate


class AnalysisGraph(QtWidgets.QWidget):
    """Draw per-move win rates from Black's perspective."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._points: tuple[tuple[int, float], ...] = ()
        self._language = "en"
        self.setMinimumHeight(126)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )

    def set_points(self, points: list[tuple[int, float]]) -> None:
        self._points = tuple(points)
        self.update()

    def set_language(self, language: str) -> None:
        self._language = language
        self.update()

    def paintEvent(self, _event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(30, 10, -10, -22)
        painter.fillRect(self.rect(), QtGui.QColor("#141a25"))
        painter.setFont(QtGui.QFont(painter.font().family(), 8))
        for value in (0.25, 0.5, 0.75):
            y = rect.bottom() - value * rect.height()
            painter.setPen(QtGui.QPen(QtGui.QColor("#343d4c"), 1, QtCore.Qt.PenStyle.DashLine))
            painter.drawLine(QtCore.QPointF(rect.left(), y), QtCore.QPointF(rect.right(), y))
            painter.setPen(QtGui.QColor("#8d98a9"))
            painter.drawText(QtCore.QRectF(0, y - 8, 25, 16), QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter, f"{int(value * 100)}%")
        painter.setPen(QtGui.QColor("#8d98a9"))
        painter.drawText(QtCore.QRectF(rect.left(), rect.bottom() + 4, 70, 16), QtCore.Qt.AlignmentFlag.AlignLeft, translate("Move", self._language))
        if not self._points:
            painter.setPen(QtGui.QColor("#8792a4"))
            painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, translate("Run a game review to build the graph", self._language))
            painter.end()
            return
        first_move = self._points[0][0]
        last_move = max(first_move + 1, self._points[-1][0])
        path = QtGui.QPainterPath()
        for index, (move, winrate) in enumerate(self._points):
            x = rect.left() + (move - first_move) / (last_move - first_move) * rect.width()
            y = rect.bottom() - min(1.0, max(0.0, winrate)) * rect.height()
            point = QtCore.QPointF(x, y)
            if index == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)
        painter.setPen(QtGui.QPen(QtGui.QColor("#63dfc6"), 2.5))
        painter.drawPath(path)
        painter.setBrush(QtGui.QColor("#e6f1ff"))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        for move, winrate in self._points:
            x = rect.left() + (move - first_move) / (last_move - first_move) * rect.width()
            y = rect.bottom() - min(1.0, max(0.0, winrate)) * rect.height()
            painter.drawEllipse(QtCore.QPointF(x, y), 2.1, 2.1)
        painter.end()
