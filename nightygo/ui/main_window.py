"""Main NightyGo application window."""

from pathlib import Path
import logging
import shlex

from PySide6 import QtCore, QtGui, QtWidgets

from nightygo.audio import StonePlacementSound
from nightygo.engine import AnalysisMove, EngineConfig, GtpEngine
from nightygo.model import BLACK, WHITE
from nightygo.materials import STONE_MATERIALS
from nightygo.game_controller import GameController
from nightygo.ui.board_widget import BoardWidget
from nightygo.ui.dock_title_bar import DockTitleBar
from nightygo.ui.game_tree_view import GameTreeView


logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    """Coordinate the Go model and board view."""

    def __init__(self) -> None:
        super().__init__()
        self._settings = QtCore.QSettings("NightyGo", "NightyGo")
        self._font_size = int(self._settings.value("font_size", 14))
        self._set_font_size(self._font_size)
        self._controller = GameController(self)
        self._controller.stateChanged.connect(self._refresh)
        self._controller.errorOccurred.connect(
            lambda message: self.statusBar().showMessage(message, 5000)
        )
        self._engine = GtpEngine(self)
        self._engine.statusChanged.connect(self._engine_status_changed)
        self._engine.ready.connect(self._engine_ready)
        self._engine.errorOccurred.connect(
            lambda message: self.statusBar().showMessage(message, 7000)
        )
        self._engine.analysisUpdated.connect(self._analysis_updated)
        self.game = self._controller.game
        self._stone_sound = StonePlacementSound(self)
        self._board = BoardWidget(self)
        self._board.set_board_material(self._settings.value("board_material", "Classic wood"))
        self._board.set_stone_material(self._settings.value("stone_material", "Traditional"))
        self._board.set_game(self.game)
        self._board.point_clicked.connect(self._play_at)

        self._undo_button = QtWidgets.QPushButton("Undo")
        self._undo_button.clicked.connect(self._undo)
        self._redo_button = QtWidgets.QPushButton("Redo")
        self._redo_button.clicked.connect(self._redo)
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
        saved_sound = self._settings.value(
            "placement_sound", StonePlacementSound.available_sounds()[0]
        )
        if saved_sound not in StonePlacementSound.available_sounds():
            logger.info("Replacing unavailable saved placement sound %r", saved_sound)
            saved_sound = StonePlacementSound.available_sounds()[0]
            self._settings.setValue("placement_sound", saved_sound)
        self._stone_sound.set_sound(saved_sound)

        self._game_tree = GameTreeView(self)
        self._game_tree.node_selected.connect(self._tree_node_selected)
        self._tree_dock = QtWidgets.QDockWidget("Game Tree", self)
        self._tree_dock.setObjectName("gameTreeDock")
        self._tree_dock.setWidget(self._game_tree)
        self._tree_dock.setTitleBarWidget(DockTitleBar(self._tree_dock))
        self._game_tree.set_stone_material(
            self._settings.value("stone_material", "Traditional")
        )

        self._analysis_status = QtWidgets.QLabel("Configure KataGo in Settings → Preferences")
        self._analysis_summary = QtWidgets.QLabel("No analysis available")
        self._analysis_summary.setWordWrap(True)
        self._candidate_list = QtWidgets.QListWidget()
        self._candidate_list.itemDoubleClicked.connect(self._play_selected_candidate)
        self._analysis_data: dict[str, AnalysisMove] = {}
        self._analysis_requested = False
        start_analysis_button = QtWidgets.QPushButton("Analyze position")
        start_analysis_button.clicked.connect(self._start_engine_analysis)
        stop_analysis_button = QtWidgets.QPushButton("Stop")
        stop_analysis_button.clicked.connect(self._stop_engine_analysis)
        play_candidate_button = QtWidgets.QPushButton("Play selected move")
        play_candidate_button.clicked.connect(self._play_selected_candidate)
        analysis_buttons = QtWidgets.QHBoxLayout()
        analysis_buttons.addWidget(start_analysis_button)
        analysis_buttons.addWidget(stop_analysis_button)
        analysis_layout = QtWidgets.QVBoxLayout()
        analysis_layout.addWidget(self._analysis_status)
        analysis_layout.addWidget(self._analysis_summary)
        analysis_layout.addWidget(self._candidate_list, 1)
        analysis_layout.addLayout(analysis_buttons)
        analysis_layout.addWidget(play_candidate_button)
        analysis_widget = QtWidgets.QWidget(self)
        analysis_widget.setLayout(analysis_layout)
        self._analysis_dock = QtWidgets.QDockWidget("AI Analysis", self)
        self._analysis_dock.setObjectName("analysisDock")
        self._analysis_dock.setWidget(analysis_widget)
        self._analysis_dock.setTitleBarWidget(DockTitleBar(self._analysis_dock))

        self._comment_editor = QtWidgets.QPlainTextEdit(self)
        self._comment_editor.setPlaceholderText("Comments for the selected move…")
        save_comment_button = QtWidgets.QPushButton("Save comment")
        save_comment_button.clicked.connect(self._save_current_comment)
        comment_layout = QtWidgets.QVBoxLayout()
        comment_layout.addWidget(self._comment_editor, 1)
        comment_layout.addWidget(save_comment_button)
        comment_widget = QtWidgets.QWidget(self)
        comment_widget.setLayout(comment_layout)
        self._comments_dock = QtWidgets.QDockWidget("Comments", self)
        self._comments_dock.setObjectName("commentsDock")
        self._comments_dock.setWidget(comment_widget)
        self._comments_dock.setTitleBarWidget(DockTitleBar(self._comments_dock))

        undo_action = QtGui.QAction("Undo", self)
        undo_action.setShortcut(QtGui.QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        self.addAction(undo_action)
        redo_action = QtGui.QAction("Redo", self)
        redo_action.setShortcut(QtGui.QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        self.addAction(redo_action)
        self._create_file_menu()
        settings_menu = self.menuBar().addMenu("Settings")
        preferences_action = settings_menu.addAction("Preferences…")
        preferences_action.triggered.connect(self._open_settings)

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(self._previous_button)
        controls.addWidget(self._next_button)
        controls.addWidget(self._variations)
        controls.addStretch(1)
        controls.addWidget(self._capture_label)
        controls.addWidget(self._undo_button)
        controls.addWidget(self._redo_button)
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
        self._controls_dock.setTitleBarWidget(DockTitleBar(self._controls_dock))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._board, 1)
        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._tree_dock)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._analysis_dock)
        self.tabifyDockWidget(self._tree_dock, self._analysis_dock)
        self._analysis_dock.hide()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self._controls_dock)
        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction(self._tree_dock.toggleViewAction())
        view_menu.addAction(self._analysis_dock.toggleViewAction())
        view_menu.addAction(self._comments_dock.toggleViewAction())
        view_menu.addAction(self._controls_dock.toggleViewAction())
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._comments_dock)
        self.tabifyDockWidget(self._tree_dock, self._comments_dock)
        self._comments_dock.hide()
        self.setWindowTitle("NightyGo")
        self.resize(860, 760)
        self.resizeDocks(
            [self._controls_dock],
            [100],
            QtCore.Qt.Orientation.Vertical,
        )
        self._set_font_size(self._font_size)
        self._create_edit_menu()
        self._board.markupRequested.connect(self._apply_markup)
        self._refresh()

    def _create_edit_menu(self) -> None:
        menu = self.menuBar().addMenu("Edit")
        game_info = menu.addAction("Game information…")
        game_info.triggered.connect(self._edit_game_info)
        comment = menu.addAction("Edit current comment")
        comment.triggered.connect(self._comments_dock.show)
        menu.addSeparator()
        mainline = menu.addAction("Make current variation the main line")
        mainline.triggered.connect(self._controller.make_current_variation_mainline)
        delete = menu.addAction("Delete current variation")
        delete.triggered.connect(self._controller.delete_current_variation)
        markup_menu = menu.addMenu("Add board markup")
        tools = (
            ("Triangle", "triangle"),
            ("Square", "square"),
            ("Circle", "circle"),
            ("Cross mark", "cross"),
            ("Text label…", "label"),
            ("Line", "line"),
            ("Arrow", "arrow"),
        )
        for label, mode in tools:
            action = markup_menu.addAction(label)
            action.triggered.connect(
                lambda _checked=False, selected=mode: self._select_markup_tool(selected)
            )

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
        if self._controller.play_at(x, y):
            self._stone_sound.play()

    def _undo(self) -> None:
        self._controller.undo()

    def _redo(self) -> None:
        self._controller.redo()

    def _pass_turn(self) -> None:
        self._controller.pass_turn()

    def _previous(self) -> None:
        self._controller.previous()

    def _next(self) -> None:
        self._controller.next(self._variations.currentIndex())

    def _new_game(self) -> None:
        sizes = ("9", "13", "19")
        preferred_size = str(self._settings.value("board_size", 19))
        if preferred_size not in sizes:
            preferred_size = "19"
        selected, accepted = QtWidgets.QInputDialog.getItem(
            self,
            "New Game",
            "Board size",
            sizes,
            sizes.index(preferred_size),
            False,
        )
        if not accepted:
            return
        board_size = int(selected)
        self._settings.setValue("board_size", board_size)
        self._controller.new_game(board_size)

    def _open_sgf(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open SGF", "", "SGF files (*.sgf *.SGF);;All files (*)"
        )
        if not path:
            return
        if self._controller.load_sgf(path) and len(self._controller.collection.games) > 1:
            self.statusBar().showMessage(
                "Loaded the first game; all game trees are preserved when saving",
                6000,
            )

    def _save_sgf(self) -> None:
        if not self._controller.current_path:
            self._save_sgf_as()
            return
        self._write_to(self._controller.current_path)

    def _save_sgf_as(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save SGF",
            self._controller.current_path or "game.sgf",
            "SGF files (*.sgf)",
        )
        if not path:
            return
        if Path(path).suffix.lower() != ".sgf":
            path += ".sgf"
        self._write_to(path)

    def _write_to(self, path: str) -> None:
        if self._controller.save_sgf(path):
            self.statusBar().showMessage(f"Saved {path}", 3000)

    def _save_current_comment(self) -> None:
        self._controller.set_current_comment(self._comment_editor.toPlainText())
        self.statusBar().showMessage("Comment saved to the current SGF node", 3000)

    def _edit_game_info(self) -> None:
        fields = (
            ("PB", "Black player"),
            ("PW", "White player"),
            ("BR", "Black rank"),
            ("WR", "White rank"),
            ("DT", "Date"),
            ("EV", "Event"),
            ("RO", "Round"),
            ("RE", "Result"),
            ("KM", "Komi"),
            ("RU", "Rules"),
            ("TM", "Time limit (seconds)"),
            ("OT", "Overtime"),
        )
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Game information")
        inputs: dict[str, QtWidgets.QLineEdit] = {}
        form = QtWidgets.QFormLayout()
        for identifier, label in fields:
            field = QtWidgets.QLineEdit(
                (self._controller.root.values(identifier) or [""])[0], dialog
            )
            inputs[identifier] = field
            form.addRow(label, field)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addLayout(form)
        layout.addWidget(buttons)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self._controller.set_game_info(
                {key: field.text() for key, field in inputs.items()}
            )

    def _select_markup_tool(self, mode: str) -> None:
        self._pending_line_start: tuple[int, int] | None = None
        self._board.set_markup_mode(mode)
        action = "two intersections" if mode in ("line", "arrow") else "an intersection"
        self.statusBar().showMessage(f"Click {action} on the board to add markup", 5000)

    def _apply_markup(self, x: int, y: int, mode: str) -> None:
        if mode in ("line", "arrow"):
            if self._pending_line_start is None:
                self._pending_line_start = (x, y)
                self.statusBar().showMessage("Select the end point", 5000)
                return
            x1, y1 = self._pending_line_start
            self._pending_line_start = None
            self._board.set_markup_mode("")
            self._controller.add_line_markup(mode, x1, y1, x, y)
            return
        label = ""
        if mode == "label":
            label, accepted = QtWidgets.QInputDialog.getText(
                self, "Board label", "Label text"
            )
            if not accepted or not label:
                return
        self._controller.add_markup(mode, x, y, label)

    def _start_engine_analysis(self) -> None:
        self._analysis_dock.show()
        if self._engine.status == GtpEngine.ANALYZING:
            self._analysis_requested = False
            self._engine.stop_analysis()
            self._analysis_status.setText("Stopping analysis…")
            return
        if self._engine.status == GtpEngine.READY:
            self._request_current_position_analysis()
            return
        program = self._settings.value("engine_program", "")
        if not program:
            self._analysis_status.setText("Choose the KataGo executable in Preferences")
            self._open_settings()
            program = self._settings.value("engine_program", "")
        if not program:
            return
        try:
            arguments = tuple(
                shlex.split(self._settings.value("engine_arguments", "gtp"))
            )
        except ValueError as error:
            self.statusBar().showMessage(f"Invalid engine arguments: {error}", 6000)
            return
        self._analysis_requested = True
        self._analysis_status.setText("Starting KataGo…")
        self._engine.start(EngineConfig(str(program), arguments))

    def _stop_engine_analysis(self) -> None:
        self._analysis_requested = False
        self._engine.stop_analysis()

    def _engine_ready(self, name: str, version: str) -> None:
        self._analysis_status.setText(f"{name} · {version}")
        if self._analysis_requested:
            self._request_current_position_analysis()

    def _engine_status_changed(self, status: str) -> None:
        if status == GtpEngine.ERROR:
            self._analysis_status.setText("Engine error; see status message")
        elif status == GtpEngine.STARTING:
            self._analysis_status.setText("Starting engine…")
        elif status == GtpEngine.STOPPED:
            self._analysis_status.setText("Engine stopped")
        elif status == GtpEngine.ANALYZING:
            self._analysis_status.setText("Analyzing current position…")

    def _request_current_position_analysis(self) -> None:
        self._analysis_requested = True
        root = self._controller.root
        try:
            komi = float((root.values("KM") or ["6.5"])[0])
        except ValueError:
            komi = 6.5
        self._engine.set_position(self.game.size, komi)
        black: list[str] = []
        white: list[str] = []
        columns = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        for y, row in enumerate(self.game.board):
            for x, color in enumerate(row):
                if color == 0:
                    continue
                vertex = f"{columns[x]}{self.game.size - y}"
                (black if color == BLACK else white).append(vertex)
        self._engine.set_stones(tuple(black), tuple(white))
        player = "B" if self.game.to_play == BLACK else "W"
        self._engine.start_analysis(player, interval_ms=500)

    def _analysis_updated(self, move: AnalysisMove) -> None:
        self._analysis_data[move.vertex] = move
        ordered = sorted(
            self._analysis_data.values(),
            key=lambda candidate: (
                candidate.order if candidate.order is not None else 999,
                -candidate.visits,
            ),
        )
        self._candidate_list.clear()
        for candidate in ordered[:10]:
            winrate = (
                f"{candidate.winrate * 100:.1f}%"
                if candidate.winrate is not None
                else "—"
            )
            score = (
                f"{candidate.score_lead:+.1f} pts"
                if candidate.score_lead is not None
                else "—"
            )
            item = QtWidgets.QListWidgetItem(
                f"{candidate.order + 1 if candidate.order is not None else '·'}  "
                f"{candidate.vertex}    {winrate}    {score}    "
                f"{candidate.visits:,} visits"
            )
            item.setData(QtCore.Qt.ItemDataRole.UserRole, candidate.vertex)
            self._candidate_list.addItem(item)
        if ordered:
            best = ordered[0]
            winrate = "—" if best.winrate is None else f"{best.winrate * 100:.1f}%"
            score = "—" if best.score_lead is None else f"{best.score_lead:+.1f} pts"
            self._analysis_summary.setText(
                f"Top move {best.vertex} · {winrate} · {score} · {best.visits:,} visits"
            )
        self._board.set_analysis_moves(
            [candidate.vertex for candidate in ordered[:8]],
            self.game.size,
        )

    def _play_selected_candidate(self, *_args) -> None:
        item = self._candidate_list.currentItem()
        if item is None:
            return
        vertex = str(item.data(QtCore.Qt.ItemDataRole.UserRole))
        columns = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        if len(vertex) < 2 or vertex[0] not in columns:
            return
        try:
            x = columns.index(vertex[0])
            y = self.game.size - int(vertex[1:])
        except ValueError:
            return
        if self._controller.play_at(x, y):
            self._stone_sound.play()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self._engine.stop()
        super().closeEvent(event)

    def _show_error(self, title: str, error: Exception) -> None:
        QtWidgets.QMessageBox.critical(self, title, str(error))

    def _open_settings(self) -> None:
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("NightyGo Preferences")
        font_size = QtWidgets.QSpinBox(dialog)
        font_size.setRange(10, 30)
        font_size.setSuffix(" pt")
        font_size.setValue(self._font_size)

        sound_selector = QtWidgets.QComboBox(dialog)
        sound_selector.addItems(StonePlacementSound.available_sounds())
        saved_sound = self._settings.value(
            "placement_sound", StonePlacementSound.available_sounds()[0]
        )
        if saved_sound in StonePlacementSound.available_sounds():
            sound_selector.setCurrentText(saved_sound)
        preview_button = QtWidgets.QPushButton("Preview", dialog)
        preview_button.clicked.connect(
            lambda: self._stone_sound.play(sound_selector.currentText())
        )
        sound_row = QtWidgets.QHBoxLayout()
        sound_row.addWidget(sound_selector, 1)
        sound_row.addWidget(preview_button)

        board_selector = QtWidgets.QComboBox(dialog)
        board_selector.addItems(BoardWidget.available_board_materials())
        board_selector.setCurrentText(
            self._settings.value("board_material", "Classic wood")
        )
        stone_selector = QtWidgets.QComboBox(dialog)
        stone_selector.addItems(STONE_MATERIALS)
        stone_selector.setCurrentText(
            self._settings.value("stone_material", "Traditional")
        )
        engine_program = QtWidgets.QLineEdit(
            self._settings.value("engine_program", ""), dialog
        )
        engine_arguments = QtWidgets.QLineEdit(
            self._settings.value("engine_arguments", "gtp"), dialog
        )
        engine_browse = QtWidgets.QPushButton("Browse…", dialog)
        engine_browse.clicked.connect(
            lambda: self._select_engine_program(engine_program)
        )
        engine_row = QtWidgets.QHBoxLayout()
        engine_row.addWidget(engine_program, 1)
        engine_row.addWidget(engine_browse)

        form = QtWidgets.QFormLayout()
        form.addRow("Application font size", font_size)
        form.addRow("Go stone placement sound", sound_row)
        form.addRow("Board texture", board_selector)
        form.addRow("Stone texture", stone_selector)
        form.addRow("KataGo executable", engine_row)
        form.addRow("Engine arguments", engine_arguments)
        source_hint = QtWidgets.QLabel("Five real Go-stone recordings from two board types.")
        source_hint.setWordWrap(True)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addLayout(form)
        layout.addWidget(source_hint)
        layout.addWidget(buttons)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        size = font_size.value()
        selected_sound = sound_selector.currentText()
        selected_board = board_selector.currentText()
        selected_stones = stone_selector.currentText()
        selected_engine = engine_program.text().strip()
        selected_arguments = engine_arguments.text().strip()
        self._settings.setValue("font_size", size)
        self._settings.setValue("placement_sound", selected_sound)
        self._settings.setValue("board_material", selected_board)
        self._settings.setValue("stone_material", selected_stones)
        self._settings.setValue("engine_program", selected_engine)
        self._settings.setValue("engine_arguments", selected_arguments)
        self._stone_sound.set_sound(selected_sound)
        self._board.set_board_material(selected_board)
        self._board.set_stone_material(selected_stones)
        self._game_tree.set_stone_material(selected_stones)
        logger.info(
            "Preferences updated: font=%d pt, board=%s, stones=%s, sound=%s",
            size,
            selected_board,
            selected_stones,
            selected_sound,
        )
        self._set_font_size(size)

    def _select_engine_program(self, field: QtWidgets.QLineEdit) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select KataGo executable",
            field.text() or str(Path.home()),
            "All files (*)",
        )
        if path:
            field.setText(path)

    def _set_font_size(self, size: int) -> None:
        self._font_size = size
        font = QtWidgets.QApplication.font()
        font.setPointSize(size)
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.setFont(font)
        self.setFont(font)
        for widget in self.findChildren(QtWidgets.QWidget):
            widget.setFont(font)
        game_tree = getattr(self, "_game_tree", None)
        if game_tree is not None:
            game_tree.set_font_size(size)

    def _refresh_navigation(self, *_args) -> None:
        self._next_button.setEnabled(self._controller.session.can_advance)

    def _tree_node_selected(self, node) -> None:
        if node is self._controller.current_node:
            return
        self._controller.navigate_to(node)

    def _refresh_tree(self) -> None:
        self._game_tree.set_tree(
            self._controller.root,
            self._controller.current_node,
            self.game.size,
        )

    def _refresh(self) -> None:
        self.game = self._controller.game
        if self._engine.status == GtpEngine.ANALYZING:
            self._analysis_requested = False
            self._engine.stop_analysis()
        self._analysis_data.clear()
        self._candidate_list.clear()
        self._analysis_summary.setText("Analysis not available for this move")
        self._board.set_analysis_moves([], self.game.size)
        self._board.set_markup(self._controller.current_node.properties)
        self._board.set_game(self.game)
        self._comment_editor.setPlainText(
            "\n".join(self._controller.current_node.values("C"))
        )
        self._refresh_tree()
        self._undo_button.setEnabled(self._controller.session.can_undo)
        self._redo_button.setEnabled(self._controller.session.can_advance)
        self._previous_button.setEnabled(self._controller.session.can_undo)
        self._variations.blockSignals(True)
        self._variations.clear()
        for index, _child in enumerate(self._controller.current_node.children, start=1):
            self._variations.addItem(f"Variation {index}")
        self._variations.setCurrentIndex(0)
        self._variations.blockSignals(False)
        self._next_button.setEnabled(self._controller.session.can_advance)
        if self.game.is_finished:
            self.statusBar().showMessage("Game ended after two passes")
        else:
            color = "Black" if self.game.to_play == BLACK else "White"
            self.statusBar().showMessage(f"{color} to play")
        self._capture_label.setText(
            f"Captured  Black: {self.game.captures[BLACK]}   White: {self.game.captures[WHITE]}"
        )
