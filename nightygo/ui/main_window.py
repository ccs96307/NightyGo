"""Main NightyGo application window."""

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from nightygo.audio import StonePlacementSound
from nightygo.model import BLACK, WHITE, IllegalMove
from nightygo.sgf import SgfCollection, SgfError, read_sgf, write_sgf
from nightygo.sgf_session import SgfGameSession
from nightygo.ui.board_widget import BoardWidget
from nightygo.ui.game_tree_view import GameTreeView


class MainWindow(QtWidgets.QMainWindow):
    """Coordinate the Go model and board view."""

    def __init__(self) -> None:
        super().__init__()
        self._collection = SgfCollection()
        self._session = SgfGameSession.new_game()
        self._collection.games.append(self._session.root)
        self.game = self._session.game
        self._current_path: str | None = None
        self._stone_sound = StonePlacementSound(self)
        self._board = BoardWidget(self)
        self._board.set_game(self.game)
        self._board.point_clicked.connect(self._play_at)

        self._undo_button = QtWidgets.QPushButton("Undo")
        self._undo_button.clicked.connect(self._undo)
        self._previous_button = QtWidgets.QPushButton("Previous")
        self._previous_button.clicked.connect(self._previous)
        self._next_button = QtWidgets.QPushButton("Next")
        self._next_button.clicked.connect(self._next)
        self._variations = QtWidgets.QComboBox()
        self._variations.setMinimumWidth(120)
        self._variations.currentIndexChanged.connect(self._refresh_navigation)
        pass_button = QtWidgets.QPushButton("Pass")
        pass_button.clicked.connect(self._pass_turn)
        self._capture_label = QtWidgets.QLabel()

        self._game_tree = GameTreeView(self)
        self._game_tree.node_selected.connect(self._tree_node_selected)
        self._tree_dock = QtWidgets.QDockWidget("Game Tree", self)
        self._tree_dock.setObjectName("gameTreeDock")
        self._tree_dock.setWidget(self._game_tree)

        undo_action = QtGui.QAction("Undo", self)
        undo_action.setShortcut(QtGui.QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        self.addAction(undo_action)
        self._create_file_menu()

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(self._previous_button)
        controls.addWidget(self._next_button)
        controls.addWidget(self._variations)
        controls.addStretch(1)
        controls.addWidget(self._capture_label)
        controls.addWidget(self._undo_button)
        controls.addWidget(pass_button)
        controls_widget = QtWidgets.QWidget(self)
        controls_widget.setLayout(controls)
        controls_widget.setMinimumHeight(72)
        controls_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self._controls_dock = QtWidgets.QDockWidget("Controls", self)
        self._controls_dock.setObjectName("controlsDock")
        self._controls_dock.setWidget(controls_widget)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._board, 1)
        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._tree_dock)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self._controls_dock)
        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction(self._tree_dock.toggleViewAction())
        view_menu.addAction(self._controls_dock.toggleViewAction())
        self.setWindowTitle("NightyGo")
        self.resize(860, 760)
        self.resizeDocks(
            [self._controls_dock],
            [100],
            QtCore.Qt.Orientation.Vertical,
        )
        self._refresh()

    def _create_file_menu(self) -> None:
        menu = self.menuBar().addMenu("File")
        new_action = menu.addAction("New Game")
        new_action.setShortcut(QtGui.QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_game)
        open_action = menu.addAction("Open SGF…")
        open_action.setShortcut(QtGui.QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_sgf)
        save_action = menu.addAction("Save SGF")
        save_action.setShortcut(QtGui.QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_sgf)
        save_as_action = menu.addAction("Save SGF As…")
        save_as_action.setShortcut(QtGui.QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_sgf_as)

    def _play_at(self, x: int, y: int) -> None:
        try:
            move = self.game.play(x, y)
            self._session.append_move(move)
        except (IllegalMove, SgfError) as error:
            self.statusBar().showMessage(str(error), 3000)
            return
        self.game = self._session.game
        self._stone_sound.play()
        self._refresh()

    def _undo(self) -> None:
        if not self._session.can_undo:
            return
        self._previous()

    def _pass_turn(self) -> None:
        try:
            move = self.game.pass_turn()
            self._session.append_move(move)
        except (IllegalMove, SgfError) as error:
            self.statusBar().showMessage(str(error), 3000)
            return
        self.game = self._session.game
        self._refresh()

    def _previous(self) -> None:
        try:
            self.game = self._session.previous()
        except SgfError as error:
            self.statusBar().showMessage(str(error), 3000)
            return
        self._refresh()

    def _next(self) -> None:
        try:
            self.game = self._session.next(self._variations.currentIndex())
        except SgfError as error:
            self.statusBar().showMessage(str(error), 3000)
            return
        self._refresh()

    def _new_game(self) -> None:
        self._session = SgfGameSession.new_game()
        self._collection = SgfCollection([self._session.root])
        self._current_path = None
        self.game = self._session.game
        self._refresh()

    def _open_sgf(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open SGF", "", "SGF files (*.sgf *.SGF);;All files (*)"
        )
        if not path:
            return
        try:
            collection = read_sgf(path)
            session = SgfGameSession(collection.games[0], start_at_end=True)
        except (OSError, SgfError, ValueError) as error:
            self._show_error("Could not open SGF", error)
            return
        self._collection = collection
        self._session = session
        self._current_path = path
        self.game = session.game
        self._refresh()
        if len(collection.games) > 1:
            self.statusBar().showMessage(
                f"Loaded first game; preserving all {len(collection.games)} games when saving", 6000
            )

    def _save_sgf(self) -> None:
        if self._current_path is None:
            self._save_sgf_as()
            return
        self._write_to(self._current_path)

    def _save_sgf_as(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save SGF", self._current_path or "game.sgf", "SGF files (*.sgf)"
        )
        if not path:
            return
        if Path(path).suffix.lower() != ".sgf":
            path += ".sgf"
        self._write_to(path)

    def _write_to(self, path: str) -> None:
        try:
            write_sgf(self._collection, path)
        except (OSError, SgfError) as error:
            self._show_error("Could not save SGF", error)
            return
        self._current_path = path
        self.statusBar().showMessage(f"Saved {path}", 3000)

    def _show_error(self, title: str, error: Exception) -> None:
        QtWidgets.QMessageBox.critical(self, title, str(error))

    def _refresh_navigation(self, *_args) -> None:
        self._next_button.setEnabled(self._session.can_advance)

    def _tree_node_selected(self, node) -> None:
        if node is self._session.current_node:
            return
        try:
            self.game = self._session.navigate_to(node)
        except SgfError as error:
            self.statusBar().showMessage(str(error), 3000)
            return
        self._refresh()

    def _refresh_tree(self) -> None:
        self._game_tree.set_tree(
            self._session.root,
            self._session.current_node,
            self.game.size,
        )

    def _refresh(self) -> None:
        self._board.set_game(self.game)
        self._refresh_tree()
        self._undo_button.setEnabled(self._session.can_undo)
        self._previous_button.setEnabled(self._session.can_undo)
        self._variations.blockSignals(True)
        self._variations.clear()
        for index, _child in enumerate(self._session.current_node.children, start=1):
            self._variations.addItem(f"Variation {index}")
        self._variations.setCurrentIndex(0)
        self._variations.blockSignals(False)
        self._next_button.setEnabled(self._session.can_advance)
        if self.game.is_finished:
            self.statusBar().showMessage("Game ended after two passes")
        else:
            color = "Black" if self.game.to_play == BLACK else "White"
            self.statusBar().showMessage(f"{color} to play")
        self._capture_label.setText(
            f"Captured  Black: {self.game.captures[BLACK]}   White: {self.game.captures[WHITE]}"
        )
