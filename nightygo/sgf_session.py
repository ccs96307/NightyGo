"""Game-position replay and navigation over an SGF variation tree."""

from __future__ import annotations

from nightygo.model import BLACK, WHITE, GoGame, Move
from nightygo.sgf import SgfError, SgfNode


class SgfGameSession:
    """Navigate or append moves while retaining the complete SGF tree."""

    def __init__(self, root: SgfNode, start_at_end: bool = False) -> None:
        self.root = root
        self.path = [root]
        if start_at_end:
            while self.current_node.children:
                self.path.append(self.current_node.children[0])
        self.game = self._rebuild_game()

    @classmethod
    def new_game(cls, size: int = 19) -> SgfGameSession:
        """Create a new FF[4] game tree."""
        root = SgfNode(
            properties={
                "GM": ["1"],
                "FF": ["4"],
                "CA": ["UTF-8"],
                "AP": ["NightyGo:0.1.0"],
                "SZ": [str(size)],
                "KM": ["6.5"],
            }
        )
        return cls(root)

    @property
    def current_node(self) -> SgfNode:
        return self.path[-1]

    @property
    def can_undo(self) -> bool:
        return len(self.path) > 1

    @property
    def can_advance(self) -> bool:
        return bool(self.current_node.children)

    def previous(self) -> GoGame:
        """Move to the parent node and rebuild the position."""
        if not self.can_undo:
            raise SgfError("Already at the start of the game")
        self.path.pop()
        self.game = self._rebuild_game()
        return self.game

    def next(self, variation_index: int = 0) -> GoGame:
        """Advance along one child variation of the current node."""
        children = self.current_node.children
        if not 0 <= variation_index < len(children):
            raise SgfError("No such variation at the current node")
        self.path.append(children[variation_index])
        self.game = self._rebuild_game()
        return self.game

    def navigate_to(self, target: SgfNode) -> GoGame:
        """Navigate directly to a node in this session's game tree."""
        path: list[SgfNode] = []

        def find(node: SgfNode) -> bool:
            path.append(node)
            if node is target:
                return True
            for child in node.children:
                if find(child):
                    return True
            path.pop()
            return False

        if not find(self.root):
            raise SgfError("The selected node is not part of this game")
        self.path = path
        self.game = self._rebuild_game()
        return self.game

    def append_move(self, move: Move) -> GoGame:
        """Append a move as a continuation or a new variation."""
        color = "B" if move.color == BLACK else "W"
        value = "" if move.point is None else _encode_point(move.point)
        node = SgfNode(properties={color: [value]})
        self.current_node.children.append(node)
        self.path.append(node)
        self.game = self._rebuild_game()
        return self.game

    def _rebuild_game(self) -> GoGame:
        size = _board_size(self.root)
        game = GoGame(size=size)
        for node in self.path:
            self._apply_setup(game, node)
            player_to_play = node.values("PL")
            if player_to_play:
                game.set_player_to_play(_color_from_sgf(player_to_play[0]))
            move_color = "B" if node.values("B") else "W" if node.values("W") else None
            if node.values("B") and node.values("W"):
                raise SgfError("A node cannot contain both B and W moves")
            if move_color is None:
                continue
            move_value = node.values(move_color)[0]
            game.set_player_to_play(_color_from_sgf(move_color))
            if move_value == "" or (move_value == "tt" and size <= 19):
                game.pass_turn()
            else:
                try:
                    x, y = _decode_point(move_value, size)
                    game.play(x, y)
                except (ValueError, IndexError) as error:
                    raise SgfError(f"Invalid {move_color} move {move_value!r}") from error
        return game

    @staticmethod
    def _apply_setup(game: GoGame, node: SgfNode) -> None:
        black = _expand_points(node.values("AB"), game.size)
        white = _expand_points(node.values("AW"), game.size)
        empty = _expand_points(node.values("AE"), game.size)
        if black or white or empty:
            game.set_setup_stones(black=black, white=white, empty=empty)


def _board_size(root: SgfNode) -> int:
    values = root.values("SZ")
    if not values:
        return 19
    value = values[0]
    if ":" in value:
        width, height = value.split(":", 1)
        if width != height:
            raise SgfError("Rectangular SGF boards are not supported yet")
        value = width
    try:
        return int(value)
    except ValueError as error:
        raise SgfError(f"Invalid board size: {value!r}") from error


def _color_from_sgf(value: str) -> int:
    normalized = value.upper()
    if normalized == "B":
        return BLACK
    if normalized == "W":
        return WHITE
    raise SgfError(f"Invalid SGF color: {value!r}")


def _decode_point(value: str, size: int) -> tuple[int, int]:
    if len(value) != 2:
        raise SgfError(f"Invalid SGF point: {value!r}")
    x, y = ord(value[0]) - ord("a"), ord(value[1]) - ord("a")
    if not (0 <= x < size and 0 <= y < size):
        raise SgfError(f"SGF point is outside the {size}x{size} board: {value!r}")
    return x, y


def _encode_point(point: tuple[int, int]) -> str:
    x, y = point
    return chr(ord("a") + x) + chr(ord("a") + y)


def _expand_points(values: list[str], size: int) -> tuple[tuple[int, int], ...]:
    points: set[tuple[int, int]] = set()
    for value in values:
        if ":" not in value:
            points.add(_decode_point(value, size))
            continue
        first, last = value.split(":", 1)
        x1, y1 = _decode_point(first, size)
        x2, y2 = _decode_point(last, size)
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                points.add((x, y))
    return tuple(sorted(points))
