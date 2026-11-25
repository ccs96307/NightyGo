"""PySide6 board renderer and pointer interaction."""

import math

from PySide6 import QtCore, QtGui, QtWidgets

from nightygo.materials import BOARD_MATERIALS, board_texture
from nightygo.model import EMPTY, GoGame
from nightygo.preview import stone_pixmap, stone_preview


class BoardWidget(QtWidgets.QWidget):
    """Draw a Go board and emit clicked intersections."""

    point_clicked = QtCore.Signal(int, int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._game: GoGame | None = None
        self._hover_point: tuple[int, int] | None = None
        self._analysis_points: tuple[tuple[int, int, int], ...] = ()
        self._board_material = "wood"
        self._stone_material = "classic"
        self._animation_phase = 0.0
        self._theme_animation_timer = QtCore.QTimer(self)
        self._theme_animation_timer.setInterval(50)
        self._theme_animation_timer.timeout.connect(self._advance_theme_animation)
        self.setMinimumSize(440, 440)
        self.setMouseTracking(True)

    @staticmethod
    def available_board_materials() -> tuple[str, ...]:
        """Return user-facing board texture names."""
        return tuple(BOARD_MATERIALS)

    def set_board_material(self, material: str) -> None:
        """Set the board surface texture and repaint."""
        if material in BOARD_MATERIALS:
            self._board_material = BOARD_MATERIALS[material]
            self._sync_theme_animation()
            self.update()

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        super().showEvent(event)
        QtCore.QTimer.singleShot(0, self._sync_theme_animation)

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        self._theme_animation_timer.stop()
        super().hideEvent(event)

    def _sync_theme_animation(self) -> None:
        if self.isVisible() and self._board_material != "wood":
            self._theme_animation_timer.start()
        else:
            self._theme_animation_timer.stop()

    def _advance_theme_animation(self) -> None:
        self._animation_phase = (self._animation_phase + 0.055) % (2 * math.pi)
        side = min(self.width(), self.height())
        surface = QtCore.QRect(
            int((self.width() - side) / 2),
            int((self.height() - side) / 2),
            side,
            side,
        )
        self.update(surface)

    def set_stone_material(self, material: str) -> None:
        """Set the material used to render placed and preview stones."""
        if material in ("Traditional", "Starfield", "Moonstone"):
            self._stone_material = {
                "Traditional": "classic",
                "Starfield": "starfield",
                "Moonstone": "moonstone",
            }[material]
            self.update()

    def set_game(self, game: GoGame) -> None:
        """Set the model snapshot to draw."""
        self._game = game
        self.update()

    def set_analysis_moves(self, vertices: list[str], board_size: int) -> None:
        """Set ranked GTP candidate vertices for lightweight board overlays."""
        columns = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        points = []
        for rank, vertex in enumerate(vertices):
            if len(vertex) < 2 or vertex[0] not in columns:
                continue
            try:
                x = columns.index(vertex[0])
                y = board_size - int(vertex[1:])
            except ValueError:
                continue
            if 0 <= x < board_size and 0 <= y < board_size:
                points.append((x, y, rank))
        self._analysis_points = tuple(points)
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
        outside_color = "#d7ad68" if self._board_material == "wood" else "#0b1021"
        painter.fillRect(self.rect(), QtGui.QColor(outside_color))
        if self._game is None:
            painter.end()
            return

        left, top, step = self._grid_geometry()
        side = min(self.width(), self.height())
        surface = QtCore.QRectF(
            (self.width() - side) / 2,
            (self.height() - side) / 2,
            side,
            side,
        )
        painter.drawImage(surface, board_texture(self._board_material))
        if self._board_material != "wood":
            self._draw_animated_sky(painter, surface)
        last = left + (self._game.size - 1) * step
        bottom = top + (self._game.size - 1) * step
        line_color = {
            "wood": "#392a1b",
            "starfield": "#a9b8df",
            "night_sky": "#c4d4e8",
        }[self._board_material]
        pen = QtGui.QPen(QtGui.QColor(line_color), max(1.0, step * 0.035))
        painter.setPen(pen)
        for index in range(self._game.size):
            offset = index * step
            painter.drawLine(QtCore.QPointF(left + offset, top), QtCore.QPointF(left + offset, bottom))
            painter.drawLine(QtCore.QPointF(left, top + offset), QtCore.QPointF(last, top + offset))

        self._draw_star_points(painter, left, top, step)
        self._draw_analysis_points(painter, left, top, step)
        diameter = step * 0.88
        for y, row in enumerate(self._game.board):
            for x, color in enumerate(row):
                if color == EMPTY:
                    continue
                center = QtCore.QPointF(left + x * step, top + y * step)
                target = QtCore.QRectF(center.x() - diameter / 2, center.y() - diameter / 2, diameter, diameter)
                shadow_center = QtCore.QPointF(
                    center.x() + diameter * 0.08,
                    center.y() + diameter * 0.15,
                )
                shadow = QtGui.QRadialGradient(
                    shadow_center,
                    diameter * 0.56,
                )
                shadow.setColorAt(0, QtGui.QColor(0, 0, 0, 125))
                shadow.setColorAt(0.55, QtGui.QColor(0, 0, 0, 70))
                shadow.setColorAt(1, QtGui.QColor(0, 0, 0, 0))
                painter.setPen(QtCore.Qt.PenStyle.NoPen)
                painter.setBrush(shadow)
                painter.drawEllipse(
                    shadow_center,
                    diameter * 0.56,
                    diameter * 0.45,
                )
                pixmap = stone_pixmap(color, self._stone_material)
                painter.drawPixmap(target, pixmap, QtCore.QRectF(pixmap.rect()))
                self._draw_sphere_lighting(painter, target)

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
                preview = stone_preview(self._game.to_play, self._stone_material)
                painter.drawPixmap(target, preview, QtCore.QRectF(preview.rect()))
        painter.end()

    def _draw_analysis_points(
        self,
        painter: QtGui.QPainter,
        left: float,
        top: float,
        step: float,
    ) -> None:
        if not self._analysis_points:
            return
        colors = ("#ffd166", "#58d6c0", "#6db8ff", "#c38cff")
        for x, y, rank in self._analysis_points:
            if self._game.board[y][x] != EMPTY:
                continue
            center = QtCore.QPointF(left + x * step, top + y * step)
            radius = step * (0.34 if rank == 0 else 0.29)
            fill = QtGui.QColor(colors[min(rank, len(colors) - 1)])
            fill.setAlpha(205 if rank == 0 else 165)
            painter.setPen(QtGui.QPen(QtGui.QColor("#f6f7fb"), max(1.0, step * 0.035)))
            painter.setBrush(fill)
            painter.drawEllipse(center, radius, radius)
            painter.setPen(QtGui.QColor("#151922"))
            font = painter.font()
            font.setBold(True)
            font.setPointSizeF(max(7.0, step * 0.28))
            painter.setFont(font)
            painter.drawText(
                QtCore.QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2),
                QtCore.Qt.AlignmentFlag.AlignCenter,
                str(rank + 1),
            )

    @staticmethod
    def _draw_sphere_lighting(painter: QtGui.QPainter, target: QtCore.QRectF) -> None:
        """Add directional highlights and edge shading at board display size."""
        diameter = target.width()
        center = target.center()
        painter.save()
        clip = QtGui.QPainterPath()
        clip.addEllipse(target)
        painter.setClipPath(clip)

        light = QtGui.QRadialGradient(
            QtCore.QPointF(center.x() - diameter * 0.2, center.y() - diameter * 0.24),
            diameter * 0.68,
        )
        light.setColorAt(0, QtGui.QColor(255, 255, 255, 82))
        light.setColorAt(0.38, QtGui.QColor(255, 255, 255, 25))
        light.setColorAt(1, QtGui.QColor(255, 255, 255, 0))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(light)
        painter.drawEllipse(target)

        shade = QtGui.QRadialGradient(
            QtCore.QPointF(center.x() + diameter * 0.34, center.y() + diameter * 0.35),
            diameter * 0.56,
        )
        shade.setColorAt(0, QtGui.QColor(0, 0, 0, 98))
        shade.setColorAt(0.52, QtGui.QColor(0, 0, 0, 30))
        shade.setColorAt(1, QtGui.QColor(0, 0, 0, 0))
        painter.setBrush(shade)
        painter.drawEllipse(target)

        specular = QtGui.QRadialGradient(
            QtCore.QPointF(center.x() - diameter * 0.24, center.y() - diameter * 0.28),
            diameter * 0.18,
        )
        specular.setColorAt(0, QtGui.QColor(255, 255, 255, 190))
        specular.setColorAt(0.42, QtGui.QColor(255, 255, 255, 95))
        specular.setColorAt(1, QtGui.QColor(255, 255, 255, 0))
        painter.setBrush(specular)
        painter.drawEllipse(
            QtCore.QRectF(
                center.x() - diameter * 0.4,
                center.y() - diameter * 0.42,
                diameter * 0.35,
                diameter * 0.25,
            )
        )

        rim = target.adjusted(diameter * 0.11, diameter * 0.11, -diameter * 0.11, -diameter * 0.11)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 125), max(0.7, diameter * 0.025)))
        painter.drawArc(rim, 38 * 16, 105 * 16)
        painter.restore()

    def _draw_animated_sky(self, painter: QtGui.QPainter, surface: QtCore.QRectF) -> None:
        """Draw inexpensive animated nebula light and softly twinkling stars."""
        painter.save()
        painter.setClipRect(surface)
        phase = self._animation_phase
        side = surface.width()
        glow_colors = (
            (QtGui.QColor(108, 77, 255, 112), QtGui.QColor(24, 191, 235, 86))
            if self._board_material == "starfield"
            else (QtGui.QColor(43, 177, 223, 102), QtGui.QColor(184, 94, 218, 78))
        )
        for index, color in enumerate(glow_colors):
            angle = phase * (0.8 if index == 0 else -0.57) + index * 2.5
            center = QtCore.QPointF(
                surface.left() + side * (0.5 + 0.3 * math.cos(angle)),
                surface.top() + side * (0.5 + 0.27 * math.sin(angle)),
            )
            gradient = QtGui.QRadialGradient(center, side * 0.36)
            gradient.setColorAt(0, color)
            edge = QtGui.QColor(color)
            edge.setAlpha(0)
            gradient.setColorAt(1, edge)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(gradient)
            painter.drawEllipse(center, side * 0.36, side * 0.36)

        # Broad, slowly bending aurora ribbons make the sky's motion visible
        # while the grid is redrawn on top and stays crisp.
        ribbon_colors = (
            (QtGui.QColor(67, 232, 225), QtGui.QColor(175, 89, 255))
            if self._board_material == "starfield"
            else (QtGui.QColor(100, 212, 244), QtGui.QColor(201, 123, 235))
        )
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        for index, color in enumerate(ribbon_colors):
            angle = phase * (0.7 if index == 0 else -0.52) + index * 2.1
            base_y = 0.38 + index * 0.23 + 0.13 * math.sin(angle)
            path = QtGui.QPainterPath(
                QtCore.QPointF(surface.left() - side * 0.12, surface.top() + side * base_y)
            )
            path.cubicTo(
                surface.left() + side * 0.25,
                surface.top() + side * (base_y - 0.2 * math.cos(angle)),
                surface.left() + side * 0.68,
                surface.top() + side * (base_y + 0.18 * math.sin(angle + 1.2)),
                surface.left() + side * 1.12,
                surface.top() + side * (base_y - 0.14 * math.cos(angle + 0.8)),
            )
            painter.setPen(
                QtGui.QPen(
                    QtGui.QColor(color.red(), color.green(), color.blue(), 9),
                    side * 0.105,
                    QtCore.Qt.PenStyle.SolidLine,
                    QtCore.Qt.PenCapStyle.RoundCap,
                )
            )
            painter.drawPath(path)
            painter.setPen(
                QtGui.QPen(
                    QtGui.QColor(color.red(), color.green(), color.blue(), 24),
                    side * 0.043,
                    QtCore.Qt.PenStyle.SolidLine,
                    QtCore.Qt.PenCapStyle.RoundCap,
                )
            )
            painter.drawPath(path)
            painter.setPen(
                QtGui.QPen(
                    QtGui.QColor(218, 250, 255, 65),
                    max(1.0, side * 0.0045),
                    QtCore.Qt.PenStyle.SolidLine,
                    QtCore.Qt.PenCapStyle.RoundCap,
                )
            )
            painter.drawPath(path)

        # A bright, short-lived meteor makes the animation immediately apparent.
        progress = (phase / (2 * math.pi) * 4) % 1.0
        if progress < 0.22:
            x = surface.left() + side * (0.08 + progress * 3.5)
            y = surface.top() + side * (0.2 + progress * 1.2)
            meteor = QtCore.QPointF(x, y)
            tail = QtCore.QPointF(x - side * 0.11, y - side * 0.055)
            painter.setPen(QtGui.QPen(QtGui.QColor(160, 203, 255, 75), max(2.0, side * 0.009)))
            painter.drawLine(tail, meteor)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 235), max(1.5, side * 0.004)))
            painter.drawPoint(meteor)

        for index in range(42):
            x = (index * 0.61803398875 + phase * 0.012) % 1.0
            y = (index * 0.75487766625 + 0.17) % 1.0
            twinkle = (1 + math.sin(phase * 3.2 + index * 2.13)) / 2
            alpha = int(25 + twinkle * 220)
            point = QtCore.QPointF(
                surface.left() + x * side,
                surface.top() + y * side,
            )
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(QtGui.QColor(230, 239, 255, alpha))
            radius = 0.7 + twinkle * 1.2
            painter.drawEllipse(point, radius, radius)
        painter.restore()

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
        star_color = {
            "wood": "#392a1b",
            "starfield": "#fff0bd",
            "night_sky": "#e5efff",
        }[self._board_material]
        radius = max(2.2, step * 0.095)
        for x in coordinates:
            for y in coordinates:
                center = QtCore.QPointF(left + x * step, top + y * step)
                # A subtle halo separates each hoshi from busy cosmic textures.
                painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 95), max(1.0, step * 0.06)))
                painter.setBrush(QtGui.QColor(255, 255, 255, 34))
                painter.drawEllipse(center, radius * 1.9, radius * 1.9)
                painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 165), max(0.8, step * 0.035)))
                painter.setBrush(QtGui.QColor(star_color))
                painter.drawEllipse(center, radius, radius)
                painter.setPen(QtCore.Qt.PenStyle.NoPen)
                painter.setBrush(QtGui.QColor(255, 255, 255, 115))
                painter.drawEllipse(
                    QtCore.QPointF(center.x() - radius * 0.2, center.y() - radius * 0.2),
                    radius * 0.28,
                    radius * 0.28,
                )
