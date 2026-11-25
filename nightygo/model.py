"""Core Go rules and mutable game state, independent of the user interface."""

from dataclasses import dataclass

BLACK = 1
EMPTY = 0
WHITE = 2

Point = tuple[int, int]
Board = tuple[tuple[int, ...], ...]


class IllegalMove(ValueError):
    """Raised when a move violates basic Go rules."""


@dataclass(frozen=True)
class Move:
    """A placed stone or pass, plus any stones captured by the move."""

    color: int
    point: Point | None
    captured: tuple[Point, ...] = ()


@dataclass(frozen=True)
class _Snapshot:
    board: Board
    to_play: int
    black_captures: int
    white_captures: int
    last_move: Move | None
    consecutive_passes: int
    is_finished: bool


class GoGame:
    """A Go position with captures, suicide checks, simple ko, and passes."""

    def __init__(self, size: int = 19) -> None:
        if size < 2 or size > 25:
            raise ValueError("Board size must be between 2 and 25")
        self.size = size
        self._board: Board = tuple(tuple(EMPTY for _ in range(size)) for _ in range(size))
        self.to_play = BLACK
        self.captures = {BLACK: 0, WHITE: 0}
        self.moves: list[Move] = []
        self.last_move: Move | None = None
        self.is_finished = False
        self._consecutive_passes = 0
        self._position_history = [self._board]
        self._undo_stack: list[_Snapshot] = []

    @property
    def board(self) -> Board:
        """Return the current immutable board snapshot, indexed as [row][column]."""
        return self._board

    @property
    def can_undo(self) -> bool:
        """Whether at least one move can be undone."""
        return bool(self._undo_stack)

    def play(self, x: int, y: int) -> Move:
        """Play at (x, y), capture surrounded groups, and advance the turn."""
        if self.is_finished:
            raise IllegalMove("The game has ended after two passes")
        if not (0 <= x < self.size and 0 <= y < self.size):
            raise IllegalMove("The point is outside the board")
        if self._board[y][x] != EMPTY:
            raise IllegalMove("The point is already occupied")

        color = self.to_play
        opponent = self._opponent(color)
        candidate = [list(row) for row in self._board]
        candidate[y][x] = color
        captured: list[Point] = []
        checked_groups: set[Point] = set()

        for neighbor in self._neighbors(x, y):
            nx, ny = neighbor
            if candidate[ny][nx] != opponent or neighbor in checked_groups:
                continue
            group, liberties = self._group_and_liberties(candidate, neighbor)
            checked_groups.update(group)
            if not liberties:
                captured.extend(group)
                for stone_x, stone_y in group:
                    candidate[stone_y][stone_x] = EMPTY

        own_group, own_liberties = self._group_and_liberties(candidate, (x, y))
        if not own_liberties:
            raise IllegalMove("Suicide moves are not allowed")

        new_board = tuple(tuple(row) for row in candidate)
        if len(self._position_history) > 1 and new_board == self._position_history[-2]:
            raise IllegalMove("The move violates the simple ko rule")

        move = Move(color, (x, y), tuple(sorted(captured)))
        self._undo_stack.append(self._snapshot())
        self._board = new_board
        self.to_play = opponent
        self.captures[color] += len(captured)
        self.moves.append(move)
        self.last_move = move
        self._consecutive_passes = 0
        self._position_history.append(new_board)
        return move

    def pass_turn(self) -> Move:
        """Pass and finish the game after two consecutive passes."""
        if self.is_finished:
            raise IllegalMove("The game has already ended")
        move = Move(self.to_play, None)
        self._undo_stack.append(self._snapshot())
        self.moves.append(move)
        self.last_move = move
        self.to_play = self._opponent(self.to_play)
        self._consecutive_passes += 1
        self.is_finished = self._consecutive_passes >= 2
        self._position_history.append(self._board)
        return move

    def undo(self) -> Move:
        """Undo the most recent move and restore the complete prior state."""
        if not self._undo_stack:
            raise IllegalMove("There are no moves to undo")
        undone = self.moves.pop()
        snapshot = self._undo_stack.pop()
        self._board = snapshot.board
        self.to_play = snapshot.to_play
        self.captures[BLACK] = snapshot.black_captures
        self.captures[WHITE] = snapshot.white_captures
        self.last_move = snapshot.last_move
        self._consecutive_passes = snapshot.consecutive_passes
        self.is_finished = snapshot.is_finished
        self._position_history.pop()
        return undone

    def _snapshot(self) -> _Snapshot:
        return _Snapshot(
            board=self._board,
            to_play=self.to_play,
            black_captures=self.captures[BLACK],
            white_captures=self.captures[WHITE],
            last_move=self.last_move,
            consecutive_passes=self._consecutive_passes,
            is_finished=self.is_finished,
        )

    @staticmethod
    def _opponent(color: int) -> int:
        return WHITE if color == BLACK else BLACK

    def _neighbors(self, x: int, y: int) -> tuple[Point, ...]:
        points = ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
        return tuple((nx, ny) for nx, ny in points if 0 <= nx < self.size and 0 <= ny < self.size)

    def _group_and_liberties(
        self, board: list[list[int]], start: Point
    ) -> tuple[set[Point], set[Point]]:
        color = board[start[1]][start[0]]
        group = {start}
        liberties: set[Point] = set()
        pending = [start]
        while pending:
            x, y = pending.pop()
            for point in self._neighbors(x, y):
                px, py = point
                value = board[py][px]
                if value == EMPTY:
                    liberties.add(point)
                elif value == color and point not in group:
                    group.add(point)
                    pending.append(point)
        return group, liberties
