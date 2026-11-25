"""Main NightyGo application window."""

from PySide6 import QtWidgets

from nightygo.audio import StonePlacementSound
from nightygo.model import BLACK, WHITE, GoGame, IllegalMove
from nightygo.ui.board_widget import BoardWidget


class MainWindow(QtWidgets.QMainWindow):
    """Coordinate the Go model and board view."""

    def __init__(self) -> None:
        super().__init__()
        self.game = GoGame()
        self._stone_sound = StonePlacementSound(self)
        self._board = BoardWidget(self)
        self._board.set_game(self.game)
        self._board.point_clicked.connect(self._play_at)

        pass_button = QtWidgets.QPushButton("Pass")
        pass_button.clicked.connect(self._pass_turn)
        self._capture_label = QtWidgets.QLabel()

        controls = QtWidgets.QHBoxLayout()
        controls.addStretch(1)
        controls.addWidget(self._capture_label)
        controls.addWidget(pass_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._board, 1)
        layout.addLayout(controls)
        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("NightyGo")
        self.resize(860, 760)
        self._refresh()

    def _play_at(self, x: int, y: int) -> None:
        try:
            self.game.play(x, y)
        except IllegalMove as error:
            self.statusBar().showMessage(str(error), 3000)
            return
        self._stone_sound.play()
        self._refresh()

    def _pass_turn(self) -> None:
        try:
            self.game.pass_turn()
        except IllegalMove as error:
            self.statusBar().showMessage(str(error), 3000)
            return
        self._refresh()

    def _refresh(self) -> None:
        self._board.set_game(self.game)
        if self.game.is_finished:
            self.statusBar().showMessage("Game ended after two passes")
        else:
            color = "Black" if self.game.to_play == BLACK else "White"
            self.statusBar().showMessage(f"{color} to play")
        self._capture_label.setText(
            f"Captured  Black: {self.game.captures[BLACK]}   White: {self.game.captures[WHITE]}"
        )
