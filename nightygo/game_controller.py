"""Presentation-independent game and SGF application controller."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6 import QtCore

from nightygo.model import BLACK, WHITE, GoGame, IllegalMove
from nightygo.sgf import (
    SgfCollection,
    SgfError,
    SgfNode,
    read_sgf,
    serialize_sgf,
    write_sgf,
)
from nightygo.sgf_session import SgfGameSession

logger = logging.getLogger(__name__)


def _encode_point(point: tuple[int, int]) -> str:
    x, y = point
    return chr(ord("a") + x) + chr(ord("a") + y)


class GameController(QtCore.QObject):
    """Own the current SGF collection and expose game actions to any UI."""

    stateChanged = QtCore.Signal()
    errorOccurred = QtCore.Signal(str)
    filePathChanged = QtCore.Signal(str)

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.session = SgfGameSession.new_game()
        self.collection = SgfCollection([self.session.root])
        self._current_path = ""
        self._last_error = ""
        self._saved_document = serialize_sgf(self.collection)

    @QtCore.Property("QVariantList", notify=stateChanged)
    def boardRows(self) -> list[list[int]]:
        return [list(row) for row in self.session.game.board]

    @QtCore.Property(int, notify=stateChanged)
    def boardSize(self) -> int:
        return self.session.game.size

    @QtCore.Property(int, notify=stateChanged)
    def toPlay(self) -> int:
        return self.session.game.to_play

    @QtCore.Property(int, notify=stateChanged)
    def blackCaptures(self) -> int:
        return self.session.game.captures[BLACK]

    @QtCore.Property(int, notify=stateChanged)
    def whiteCaptures(self) -> int:
        return self.session.game.captures[WHITE]

    @QtCore.Property(int, notify=stateChanged)
    def moveCount(self) -> int:
        return len(self.session.game.moves)

    @QtCore.Property(bool, notify=stateChanged)
    def canUndo(self) -> bool:
        return self.session.can_undo

    @QtCore.Property(bool, notify=stateChanged)
    def canRedo(self) -> bool:
        return self.session.can_advance

    @QtCore.Property(bool, notify=stateChanged)
    def gameFinished(self) -> bool:
        return self.session.game.is_finished

    @QtCore.Property(str, notify=filePathChanged)
    def currentPath(self) -> str:
        return self._current_path

    @QtCore.Property(bool, notify=stateChanged)
    def isDirty(self) -> bool:
        return serialize_sgf(self.collection) != self._saved_document

    @QtCore.Property(str, notify=stateChanged)
    def currentPlayerName(self) -> str:
        color = "PB" if self.session.game.to_play == BLACK else "PW"
        values = self.session.root.values(color)
        return values[0] if values else ("Black" if color == "PB" else "White")

    @QtCore.Property(str, notify=stateChanged)
    def otherPlayerName(self) -> str:
        color = "PW" if self.session.game.to_play == BLACK else "PB"
        values = self.session.root.values(color)
        return values[0] if values else ("White" if color == "PW" else "Black")

    @property
    def game(self) -> GoGame:
        return self.session.game

    @property
    def root(self) -> SgfNode:
        return self.session.root

    @property
    def current_node(self) -> SgfNode:
        return self.session.current_node

    @property
    def current_path(self) -> str:
        return self._current_path

    @property
    def last_error(self) -> str:
        return self._last_error

    def new_game(self, board_size: int = 19) -> None:
        self.session = SgfGameSession.new_game(board_size)
        self.collection = SgfCollection([self.session.root])
        self._current_path = ""
        self._saved_document = serialize_sgf(self.collection)
        self.filePathChanged.emit("")
        self._publish()

    @QtCore.Slot(int, int, result=bool)
    def play_at(self, x: int, y: int) -> bool:
        try:
            move = self.session.game.play(x, y)
            self.session.append_move(move)
        except (IllegalMove, SgfError) as error:
            logger.debug("Rejected move at (%d, %d): %s", x, y, error)
            self._emit_error(str(error))
            return False
        self._publish()
        return True

    @QtCore.Slot(result=bool)
    def pass_turn(self) -> bool:
        try:
            move = self.session.game.pass_turn()
            self.session.append_move(move)
        except (IllegalMove, SgfError) as error:
            self._emit_error(str(error))
            return False
        self._publish()
        return True

    @QtCore.Slot(result=bool)
    def undo(self) -> bool:
        return self._navigate(self.session.previous)

    @QtCore.Slot(result=bool)
    def redo(self) -> bool:
        return self._navigate(self.session.next)

    @QtCore.Slot(result=bool)
    def previous(self) -> bool:
        return self._navigate(self.session.previous)

    @QtCore.Slot(int, result=bool)
    def next(self, variation_index: int = 0) -> bool:
        try:
            self.session.next(variation_index)
        except SgfError as error:
            self._emit_error(str(error))
            return False
        self._publish()
        return True

    @QtCore.Slot(object, result=bool)
    def navigate_to(self, node: SgfNode) -> bool:
        try:
            self.session.navigate_to(node)
        except SgfError as error:
            self._emit_error(str(error))
            return False
        self._publish()
        return True

    def load_sgf(self, path: str | Path) -> bool:
        try:
            collection = read_sgf(path)
            session = SgfGameSession(collection.games[0], start_at_end=True)
        except (OSError, SgfError, ValueError) as error:
            self._emit_error(f"Could not open SGF: {error}")
            logger.exception("Could not open SGF %s", path)
            return False
        self.collection = collection
        self.session = session
        self._saved_document = serialize_sgf(collection)
        self._current_path = str(path)
        self.filePathChanged.emit(self._current_path)
        self._publish()
        logger.info("Opened SGF %s (%d game tree(s))", path, len(collection.games))
        return True

    def save_sgf(self, path: str | Path | None = None) -> bool:
        destination = str(path) if path is not None else self._current_path
        if not destination:
            self._emit_error("Choose a path to save this game")
            return False
        try:
            write_sgf(self.collection, destination)
        except (OSError, SgfError) as error:
            self._emit_error(f"Could not save SGF: {error}")
            logger.exception("Could not save SGF %s", destination)
            return False
        self._saved_document = serialize_sgf(self.collection)
        self._current_path = destination
        self.filePathChanged.emit(destination)
        self._publish()
        logger.info("Saved SGF %s", destination)
        return True

    def save_recovery(self, path: str | Path) -> None:
        """Write a crash-recovery snapshot without changing the document path."""
        write_sgf(self.collection, path)

    def load_recovery(self, path: str | Path) -> bool:
        """Load a recovery copy and keep it marked as unsaved work."""
        try:
            collection = read_sgf(path)
            session = SgfGameSession(collection.games[0], start_at_end=True)
        except (OSError, SgfError, ValueError) as error:
            self._emit_error(f"Could not restore recovery file: {error}")
            return False
        self.collection = collection
        self.session = session
        self._current_path = ""
        self._saved_document = ""
        self.filePathChanged.emit("")
        self._publish()
        return True

    @QtCore.Slot(str, str)
    def set_root_property(self, identifier: str, value: str) -> None:
        """Set a game-info property in the root SGF node."""
        if not identifier or not identifier.isupper():
            self._emit_error(f"Invalid SGF property identifier: {identifier}")
            return
        if value:
            self.session.root.properties[identifier] = [value]
        else:
            self.session.root.properties.pop(identifier, None)
        self._publish()

    def set_game_info(self, values: dict[str, str]) -> None:
        """Update standard SGF root metadata in one state change."""
        allowed = {"PB", "PW", "BR", "WR", "DT", "EV", "RO", "RE", "KM", "RU", "TM", "OT"}
        invalid = next((identifier for identifier in values if identifier not in allowed), None)
        if invalid is not None:
            self._emit_error(f"Unsupported game-info property: {invalid}")
            return
        for identifier, value in values.items():
            if value.strip():
                self.session.root.properties[identifier] = [value.strip()]
            else:
                self.session.root.properties.pop(identifier, None)
        self._publish()

    @QtCore.Slot(str)
    def set_current_comment(self, comment: str) -> None:
        """Edit the SGF comment on the current node."""
        if comment:
            self.session.current_node.properties["C"] = [comment]
        else:
            self.session.current_node.properties.pop("C", None)
        self._publish()

    @QtCore.Slot(str, int, int, str)
    def add_markup(self, kind: str, x: int, y: int, label: str = "") -> None:
        """Add an SGF point annotation to the current node."""
        identifiers = {
            "triangle": "TR",
            "square": "SQ",
            "circle": "CR",
            "cross": "MA",
        }
        identifier = "LB" if kind == "label" else identifiers.get(kind)
        if identifier is None:
            self._emit_error(f"Unsupported markup type: {kind}")
            return
        try:
            point = _encode_point((x, y))
            if not (0 <= x < self.game.size and 0 <= y < self.game.size):
                raise ValueError("Markup point is outside the board")
        except ValueError as error:
            self._emit_error(str(error))
            return
        value = f"{point}:{label}" if kind == "label" else point
        values = self.session.current_node.properties.setdefault(identifier, [])
        if value not in values:
            values.append(value)
        self._publish()

    @QtCore.Slot(str, int, int, int, int)
    def add_line_markup(self, kind: str, x1: int, y1: int, x2: int, y2: int) -> None:
        """Add an SGF line or arrow between two board points."""
        identifier = {"line": "LN", "arrow": "AR"}.get(kind)
        if identifier is None:
            self._emit_error(f"Unsupported line markup type: {kind}")
            return
        if not all(0 <= x < self.game.size and 0 <= y < self.game.size for x, y in ((x1, y1), (x2, y2))):
            self._emit_error("Markup point is outside the board")
            return
        value = f"{_encode_point((x1, y1))}:{_encode_point((x2, y2))}"
        values = self.session.current_node.properties.setdefault(identifier, [])
        if value not in values:
            values.append(value)
        self._publish()

    @QtCore.Slot()
    def delete_current_variation(self) -> bool:
        """Delete the current node and its descendants, returning to its parent."""
        if len(self.session.path) <= 1:
            self._emit_error("The root position cannot be deleted")
            return False
        node = self.session.current_node
        parent = self.session.path[-2]
        parent.children.pop(next(i for i, child in enumerate(parent.children) if child is node))
        self.session.navigate_to(parent)
        self._publish()
        return True

    @QtCore.Slot(result=bool)
    def make_current_variation_mainline(self) -> bool:
        """Move the current variation to the first-child (main line) position."""
        if len(self.session.path) <= 1:
            self._emit_error("The root position has no parent variation")
            return False
        node = self.session.current_node
        parent = self.session.path[-2]
        index = next(i for i, child in enumerate(parent.children) if child is node)
        if index:
            parent.children.insert(0, parent.children.pop(index))
            self._publish()
        return True

    def _navigate(self, callback) -> bool:
        try:
            callback()
        except SgfError as error:
            self._emit_error(str(error))
            return False
        self._publish()
        return True

    def _emit_error(self, message: str) -> None:
        self._last_error = message
        self.errorOccurred.emit(message)

    def _publish(self) -> None:
        self._last_error = ""
        self.stateChanged.emit()
