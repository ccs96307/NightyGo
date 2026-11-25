"""PySide6 board renderer and pointer interaction."""

from PySide6 import QtCore, QtGui, QtWidgets

from nightygo.model import EMPTY, GoGame
from nightygo.preview import stone_pixmap, stone_preview


class BoardWidget(QtWidgets.QWidget):
    """Draw a Go board and emit clicked intersections."""

    point_clicked = QtCore.Signal(int, int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._game: GoGame | None = None
        self._hover_point: tuple[int, int] | None = None
        self.setMinimumSize(440, 440)
        self.setMouseTracking(True)

    def set_game(self, game: GoGame) -> None:
        """Set the model snapshot to draw."""
        self._game = game
        self.update()

    def _grid_geometry(self) -> tuple[float, float, float]:
        size = self._game.size if self._game else 19
        side = min(self.width(), self.height())
        margin = side * 0.075
        span = max(0.0, side - 2 * margin)
        step = span / max(1, size - 1)
        left = (self.width() - side) / 2 + margin
        top = (self.height() - side) / 2 + margin
        return left, top, step

    def _point_at(self, position: QtCore.QPointF | QtCore.QPoint) -> tuple[int, int] | None:
        if self._game is None:
            return None
        left, top, step = self._grid_geometry()
        if step <= 0:
            return None
        x = round((position.x() - left) / step)
        y = round((position.y() - top) / step)
        if not (0 <= x < self._game.size and 0 <= y < self._game.size):
            return None
        if abs(position.x() - (left + x * step)) > step * 0.48:
            return None
        if abs(position.y() - (top + y * step)) > step * 0.48:
            return None
        return x, y

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        point = self._point_at(event.position())
        if point is not None and self._game.board[point[1]][point[0]] != EMPTY:
            point = None
        if point != self._hover_point:
            self._hover_point = point
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        self._hover_point = None
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            point = self._point_at(event.position())
            if point is not None:
                self.point_clicked.emit(*point)
        super().mousePressEvent(event)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QtGui.QColor("#d7ad68"))
        if self._game is None:
            painter.end()
            return

        left, top, step = self._grid_geometry()
        last = left + (self._game.size - 1) * step
        bottom = top + (self._game.size - 1) * step
        pen = QtGui.QPen(QtGui.QColor("#392a1b"), max(1.0, step * 0.035))
        painter.setPen(pen)
        for index in range(self._game.size):
            offset = index * step
            painter.drawLine(QtCore.QPointF(left + offset, top), QtCore.QPointF(left + offset, bottom))
            painter.drawLine(QtCore.QPointF(left, top + offset), QtCore.QPointF(last, top + offset))

        self._draw_star_points(painter, left, top, step)
        diameter = step * 0.88
        for y, row in enumerate(self._game.board):
            for x, color in enumerate(row):
                if color == EMPTY:
                    continue
                center = QtCore.QPointF(left + x * step, top + y * step)
                target = QtCore.QRectF(center.x() - diameter / 2, center.y() - diameter / 2, diameter, diameter)
                pixmap = stone_pixmap(color)
                painter.drawPixmap(target, pixmap, QtCore.QRectF(pixmap.rect()))

        move = self._game.last_move
        if move is not None and move.point is not None:
            x, y = move.point
            center = QtCore.QPointF(left + x * step, top + y * step)
            marker = step * 0.24
            painter.setPen(QtGui.QPen(QtGui.QColor("#c52b23"), max(1.5, step * 0.055)))
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, marker, marker)

        if self._hover_point is not None:
            x, y = self._hover_point
            if self._game.board[y][x] == EMPTY:
                center = QtCore.QPointF(left + x * step, top + y * step)
                target = QtCore.QRectF(center.x() - diameter / 2, center.y() - diameter / 2, diameter, diameter)
                preview = stone_preview(self._game.to_play)
                painter.drawPixmap(target, preview, QtCore.QRectF(preview.rect()))
        painter.end()

    def _draw_star_points(self, painter: QtGui.QPainter, left: float, top: float, step: float) -> None:
        size = self._game.size
        if size == 19:
            coordinates = (3, 9, 15)
        elif size == 13:
            coordinates = (3, 6, 9)
        elif size == 9:
            coordinates = (2, 4, 6)
        else:
            coordinates = (size // 2,)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor("#392a1b"))
        radius = max(1.5, step * 0.065)
        for x in coordinates:
            for y in coordinates:
                painter.drawEllipse(QtCore.QPointF(left + x * step, top + y * step), radius, radius)
