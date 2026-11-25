"""A graphical SGF tree with vertical move lines and visible forks."""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from nightygo.model import BLACK, WHITE
from nightygo.sgf import SgfNode


class _MoveItem(QtWidgets.QGraphicsObject):
    clicked = QtCore.Signal(object)

    def __init__(
        self,
        node: SgfNode,
        move_number: int,
        color: int | None,
        selected: bool,
        tooltip: str,
    ) -> None:
        super().__init__()
        self.node = node
        self.move_number = move_number
        self.color = color
        self.selected = selected
        self.setToolTip(tooltip)
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        self.setZValue(1)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(-13, -13, 26, 26)

    def paint(self, painter, _option, _widget=None) -> None:
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        if self.color == BLACK:
            fill = QtGui.QColor("#171512")
            text = QtGui.QColor("#ffffff")
        elif self.color == WHITE:
            fill = QtGui.QColor("#fffdf8")
            text = QtGui.QColor("#24211d")
        else:
            fill = QtGui.QColor("#e0b96f")
            text = QtGui.QColor("#24211d")
        border = QtGui.QColor("#d65332" if self.selected else "#443a30")
        painter.setPen(QtGui.QPen(border, 3 if self.selected else 1.2))
        painter.setBrush(fill)
        painter.drawEllipse(self.boundingRect().adjusted(1, 1, -1, -1))
        if self.move_number:
            painter.setPen(text)
            font = painter.font()
            font.setPointSizeF(7.5 if self.move_number < 100 else 6.5)
            painter.setFont(font)
            painter.drawText(self.boundingRect(), QtCore.Qt.AlignmentFlag.AlignCenter,
                             str(self.move_number))

    def mousePressEvent(self, event) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit(self.node)
            event.accept()
            return
        super().mousePressEvent(event)


class GameTreeView(QtWidgets.QGraphicsView):
    """Draw move sequences vertically and fork only where SGF branches."""

    node_selected = QtCore.Signal(object)
    _X_SPACING = 76.0
    _Y_SPACING = 58.0

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

    def set_tree(self, root: SgfNode, current: SgfNode, board_size: int) -> None:
        """Replace the drawing with the supplied SGF tree and selection."""
        self._scene.clear()
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
            positions[key] = (x * self._X_SPACING, depth * self._Y_SPACING)
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
                path = QtGui.QPainterPath(QtCore.QPointF(parent_x, parent_y + 12))
                if abs(parent_x - child_x) < 0.01:
                    path.lineTo(child_x, child_y - 12)
                else:
                    middle_y = (parent_y + child_y) / 2
                    path.cubicTo(parent_x, middle_y, child_x, middle_y, child_x, child_y - 12)
                pen = QtGui.QPen(QtGui.QColor("#8d8375"), 1.8)
                self._scene.addPath(path, pen)

        for node in _walk_nodes(root):
            key = id(node)
            number, color = metadata[key]
            move_value = node.values("B") or node.values("W")
            details = [f"Move {number}" if number else "Start"]
            if color is not None:
                details.append("Black" if color == BLACK else "White")
                point = move_value[0]
                if not point or (point == "tt" and board_size <= 19):
                    details.append("Pass")
                else:
                    details.append(_format_point(point, board_size))
            comments = node.values("C")
            if comments:
                details.append(" ".join(comments))
            item = _MoveItem(node, number if color is not None else 0, color,
                             node is current, " · ".join(details))
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
