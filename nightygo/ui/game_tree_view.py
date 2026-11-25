"""A graphical SGF tree with vertical move lines and visible forks."""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from nightygo.model import BLACK, WHITE
from nightygo.preview import stone_pixmap
from nightygo.sgf import SgfNode
from nightygo.i18n import translate


class _MoveItem(QtWidgets.QGraphicsObject):
    clicked = QtCore.Signal(object)

    def __init__(
        self,
        node: SgfNode,
        move_number: int,
        color: int | None,
        selected: bool,
        tooltip: str,
        font_size: int,
        stone_material: str,
        accent: QtGui.QColor,
    ) -> None:
        super().__init__()
        self.node = node
        self.move_number = move_number
        self.color = color
        self.selected = selected
        self.font_size = font_size
        self.stone_material = stone_material
        self.accent = accent
        self.radius = max(12.0, font_size * 0.9)
        self.setToolTip(tooltip)
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        self.setZValue(1)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(-self.radius, -self.radius, self.radius * 2, self.radius * 2)

    def paint(self, painter, _option, _widget=None) -> None:
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        if self.color is None:
            painter.setPen(QtGui.QPen(QtGui.QColor("#756550"), 1.5))
            painter.setBrush(QtGui.QColor("#e0b96f"))
            painter.drawEllipse(self.boundingRect().adjusted(4, 4, -4, -4))
        else:
            image = stone_pixmap(self.color, self.stone_material)
            image_rect = self.boundingRect().adjusted(1, 1, -1, -1)
            painter.drawPixmap(image_rect, image, QtCore.QRectF(image.rect()))
        if self.selected:
            halo = QtGui.QColor(self.accent)
            halo.setAlpha(48)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(halo)
            painter.drawEllipse(self.boundingRect().adjusted(-3, -3, 3, 3))
            painter.setPen(QtGui.QPen(self.accent, 2.5))
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.boundingRect().adjusted(0, 0, 0, 0))
        if self.move_number and self.color is not None:
            text = QtGui.QColor("#fffdf8" if self.color == BLACK else "#24211d")
            painter.setPen(text)
            font = painter.font()
            font.setPointSizeF(max(8.0, self.font_size * 0.52))
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(
                self.boundingRect(),
                QtCore.Qt.AlignmentFlag.AlignCenter,
                str(self.move_number),
            )

    def mousePressEvent(self, event) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit(self.node)
            event.accept()
            return
        super().mousePressEvent(event)


class GameTreeView(QtWidgets.QGraphicsView):
    """Draw move sequences vertically and fork only where SGF branches."""

    node_selected = QtCore.Signal(object)
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMinimumWidth(210)
        self.setBackgroundBrush(QtGui.QColor("#faf8f3"))
        self._font_size = 14
        self._stone_material = "classic"
        self._root = None
        self._current = None
        self._board_size = 19
        self._language = "en"
        self._theme = "Dark"
        self._accent = QtGui.QColor("#69e2cf")
        self._connector = QtGui.QColor("#506178")
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

    def set_theme(self, theme: str) -> None:
        self._theme = theme
        dark = theme != "Warm light"
        self._accent = QtGui.QColor("#69e2cf" if dark else "#087e76")
        self._connector = QtGui.QColor("#506178" if dark else "#aebac7")
        self.setBackgroundBrush(QtGui.QColor("#0e1621" if dark else "#f3f6f9"))
        if self._root is not None:
            self.set_tree(self._root, self._current, self._board_size)

    def set_language(self, language: str) -> None:
        self._language = language
        if self._root is not None:
            self.set_tree(self._root, self._current, self._board_size)

    def set_font_size(self, size: int) -> None:
        """Resize move labels and nodes with the application font setting."""
        self._font_size = size
        if self._root is not None:
            self.set_tree(self._root, self._current, self._board_size)

    def set_stone_material(self, material: str) -> None:
        """Set the material used for move markers in the tree."""
        self._stone_material = {
            "Traditional": "classic",
            "Starfield": "starfield",
            "Moonstone": "moonstone",
        }.get(material, "classic")
        if self._root is not None:
            self.set_tree(self._root, self._current, self._board_size)

    def set_tree(self, root: SgfNode, current: SgfNode, board_size: int) -> None:
        """Replace the drawing with the supplied SGF tree and selection."""
        self._root = root
        self._current = current
        self._board_size = board_size
        self._scene.clear()
        diameter = max(24.0, self._font_size * 1.8)
        node_radius = max(12.0, self._font_size * 0.9)
        x_spacing = diameter + 48.0
        y_spacing = diameter + 32.0
        positions: dict[int, tuple[float, float]] = {}
        metadata: dict[int, tuple[int, int | None]] = {}
        widths: dict[int, float] = {}

        def subtree_width(node: SgfNode) -> float:
            key = id(node)
            if key not in widths:
                if len(node.children) <= 1:
                    widths[key] = max(
                        1.0,
                        subtree_width(node.children[0]) if node.children else 1.0,
                    )
                else:
                    widths[key] = sum(subtree_width(child) for child in node.children)
                    widths[key] += 0.65 * (len(node.children) - 1)
            return widths[key]

        def place(node: SgfNode, x: float, depth: int, move_number: int) -> None:
            key = id(node)
            positions[key] = (x * x_spacing, depth * y_spacing)
            black = node.values("B")
            white = node.values("W")
            color = BLACK if black else WHITE if white else None
            number = move_number + (1 if color is not None else 0)
            metadata[key] = (number, color)
            if len(node.children) == 1:
                place(node.children[0], x, depth + 1, number)
            elif node.children:
                total = subtree_width(node)
                left = x - total / 2
                for child in node.children:
                    child_width = subtree_width(child)
                    child_x = left + child_width / 2
                    place(child, child_x, depth + 1, number)
                    left += child_width + 0.65

        place(root, 0.0, 0, 0)

        for parent in _walk_nodes(root):
            parent_x, parent_y = positions[id(parent)]
            for child in parent.children:
                child_x, child_y = positions[id(child)]
                path = QtGui.QPainterPath(
                    QtCore.QPointF(parent_x, parent_y + node_radius)
                )
                if abs(parent_x - child_x) < 0.01:
                    path.lineTo(child_x, child_y - node_radius)
                else:
                    middle_y = (parent_y + child_y) / 2
                    path.cubicTo(
                        parent_x,
                        middle_y,
                        child_x,
                        middle_y,
                        child_x,
                        child_y - node_radius,
                    )
                pen = QtGui.QPen(self._connector, 1.8)
                self._scene.addPath(path, pen)

        for node in _walk_nodes(root):
            key = id(node)
            number, color = metadata[key]
            move_value = node.values("B") or node.values("W")
            details = [
                translate("Move {number}", self._language, number=number)
                if number
                else translate("Start", self._language)
            ]
            if color is not None:
                details.append(translate("Black" if color == BLACK else "White", self._language))
                point = move_value[0]
                if not point or (point == "tt" and board_size <= 19):
                    details.append(translate("Pass", self._language))
                else:
                    details.append(_format_point(point, board_size))
            comments = node.values("C")
            if comments:
                details.append(" ".join(comments))
            item = _MoveItem(
                node,
                number if color is not None else 0,
                color,
                node is current,
                " · ".join(details),
                self._font_size,
                self._stone_material,
                self._accent,
            )
            item.setPos(*positions[key])
            item.clicked.connect(self.node_selected)
            self._scene.addItem(item)

        self._scene.setSceneRect(self._scene.itemsBoundingRect().adjusted(-30, -30, 30, 30))
        selected_items = [
            item for item in self._scene.items()
            if isinstance(item, _MoveItem) and item.node is current
        ]
        if selected_items:
            self.centerOn(selected_items[0])


def _walk_nodes(root: SgfNode):
    pending = [root]
    while pending:
        node = pending.pop()
        yield node
        pending.extend(reversed(node.children))


def _format_point(value: str, board_size: int) -> str:
    x = ord(value[0]) - ord("a")
    y = ord(value[1]) - ord("a")
    column = chr(ord("A") + x + (1 if x >= 8 else 0))
    return f"{column}{board_size - y}"
