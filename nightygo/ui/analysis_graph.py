"""Compact, high-contrast win-rate history graph."""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets
from nightygo.i18n import translate


class AnalysisGraph(QtWidgets.QWidget):
    """Draw per-move win rates from Black's perspective."""

    move_selected = QtCore.Signal(int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._points: tuple[tuple[int, float], ...] = ()
        self._language = "en"
        self._theme = "Dark"
        self._font_size = 14
        self._current_move: int | None = None
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
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

    def set_theme(self, theme: str) -> None:
        self._theme = theme
        self.update()

    def set_font_size(self, size: int) -> None:
        self._font_size = size
        self.update()

    def set_current_move(self, move: int | None) -> None:
        self._current_move = move
        self.update()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self._points:
            first = self._points[0][0]
            last = max(first + 1, self._points[-1][0])
            rect = self.rect().adjusted(30, 10, -10, -22)
            move = round(first + (event.position().x() - rect.left()) / max(1, rect.width()) * (last - first))
            move = min(last, max(first, move))
            self.move_selected.emit(move)
        super().mousePressEvent(event)

    def paintEvent(self, _event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(30, 10, -10, -22)
        dark = self._theme != "Warm light"
        panel = QtGui.QColor("#0f1722" if dark else "#f4f7fa")
        guide = QtGui.QColor("#2b3848" if dark else "#d7e0e9")
        label = QtGui.QColor("#98a8bc" if dark else "#68788b")
        painter.fillRect(self.rect(), panel)
        painter.setFont(QtGui.QFont(painter.font().family(), max(8, round(self._font_size * 0.58))))
        for value in (0.25, 0.5, 0.75):
            y = rect.bottom() - value * rect.height()
            painter.setPen(QtGui.QPen(guide, 1, QtCore.Qt.PenStyle.DashLine))
            painter.drawLine(QtCore.QPointF(rect.left(), y), QtCore.QPointF(rect.right(), y))
            painter.setPen(label)
            painter.drawText(QtCore.QRectF(0, y - 8, 25, 16), QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter, f"{int(value * 100)}%")
        painter.setPen(label)
        painter.drawText(QtCore.QRectF(rect.left(), rect.bottom() + 4, 70, 16), QtCore.Qt.AlignmentFlag.AlignLeft, translate("Move", self._language))
        if not self._points:
            painter.setPen(label)
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
        if self._current_move is not None:
            selected = min(self._points, key=lambda item: abs(item[0] - self._current_move))
            x = rect.left() + (selected[0] - first_move) / (last_move - first_move) * rect.width()
            y = rect.bottom() - min(1.0, max(0.0, selected[1])) * rect.height()
            painter.setPen(QtGui.QPen(QtGui.QColor("#ffd166"), 1.5, QtCore.Qt.PenStyle.DashLine))
            painter.drawLine(QtCore.QPointF(x, rect.top()), QtCore.QPointF(x, rect.bottom()))
            painter.setBrush(QtGui.QColor("#ffd166"))
            painter.setPen(QtGui.QPen(QtGui.QColor("#0f1722"), 1.5))
            painter.drawEllipse(QtCore.QPointF(x, y), 5, 5)
        painter.end()
