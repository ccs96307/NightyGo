"""Main NightyGo application window."""

from pathlib import Path
import logging
import shlex

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtQuickWidgets import QQuickWidget

from nightygo.audio import StonePlacementSound
from nightygo.engine import AnalysisMove, AnalysisRoot, EngineConfig, GtpEngine
from nightygo.model import BLACK, WHITE
from nightygo.materials import STONE_MATERIALS
from nightygo.game_controller import GameController
from nightygo.ui.board_widget import BoardWidget
from nightygo.ui.dock_title_bar import DockTitleBar
from nightygo.ui.game_tree_view import GameTreeView
from nightygo.ui.analysis_graph import AnalysisGraph
from nightygo.sgf_session import SgfGameSession
from nightygo.library import GameLibrary
from nightygo.model_center import ModelCenterDialog, apply_model_argument


logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    """Coordinate the Go model and board view."""

    def __init__(self) -> None:
        super().__init__()
        self._settings = QtCore.QSettings("NightyGo", "NightyGo")
        self._library = GameLibrary(self._settings)
        self._font_size = int(self._settings.value("font_size", 14))
        self._ui_theme = str(self._settings.value("ui_theme", "Dark"))
        self._apply_theme(self._ui_theme)
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
        self._engine.rootInfoUpdated.connect(self._root_info_updated)
        self._engine.ownershipUpdated.connect(self._ownership_updated)
        self._engine.responseReceived.connect(self._engine_response_received)
        self.game = self._controller.game
        self._stone_sound = StonePlacementSound(self)
        self._board = BoardWidget(self)
        self._board.set_board_material(self._settings.value("board_material", "Classic wood"))
        self._board.set_stone_material(self._settings.value("stone_material", "Traditional"))
        self._board.set_animations_enabled(
            self._settings.value("animations_enabled", True, type=bool)
        )
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
        self._review_positions: list[tuple[tuple[tuple[int, ...], ...], int, int, object]] = []
        self._review_results: list[tuple[int, float]] = []
        self._review_stones_command: int | None = None
        self._review_waiting_analysis_response = False
        self._reviewing = False
        self._review_index = 0
        self._review_timer = QtCore.QTimer(self)
        self._review_timer.setSingleShot(True)
        self._review_timer.setInterval(1200)
        self._review_timer.timeout.connect(self._stop_review_sample)
        self._show_ownership = QtWidgets.QCheckBox("Ownership overlay")
        self._show_ownership.toggled.connect(lambda shown: self._board.set_ownership(
            self._latest_ownership if shown else (), self.game.size if shown else 0
        ))
        self._latest_ownership: tuple[float, ...] = ()
        self._analysis_graph = AnalysisGraph(self)
        review_button = QtWidgets.QPushButton("Review full game")
        review_button.clicked.connect(self._start_game_review)
        self._review_stop_button = QtWidgets.QPushButton("Stop review")
        self._review_stop_button.clicked.connect(self._stop_game_review)
        self._review_stop_button.setEnabled(False)
        self._review_findings = QtWidgets.QListWidget(self)
        self._review_findings.itemClicked.connect(self._jump_to_review_move)
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
        analysis_layout.addWidget(self._analysis_graph)
        analysis_layout.addWidget(self._show_ownership)
        analysis_layout.addWidget(self._candidate_list, 1)
        analysis_layout.addLayout(analysis_buttons)
        analysis_layout.addWidget(play_candidate_button)
        review_buttons = QtWidgets.QHBoxLayout()
        review_buttons.addWidget(review_button)
        review_buttons.addWidget(self._review_stop_button)
        analysis_layout.addLayout(review_buttons)
        analysis_layout.addWidget(self._review_findings)
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

        self._library_search = QtWidgets.QLineEdit(self)
        self._library_search.setPlaceholderText("Search players, event, result, or tags")
        self._library_search.textChanged.connect(self._refresh_library)
        self._library_list = QtWidgets.QListWidget(self)
        self._library_list.itemDoubleClicked.connect(self._open_library_item)
        tag_button = QtWidgets.QPushButton("Edit tags…", self)
        tag_button.clicked.connect(self._edit_library_tags)
        library_layout = QtWidgets.QVBoxLayout()
        library_layout.addWidget(self._library_search)
        library_layout.addWidget(self._library_list, 1)
        library_layout.addWidget(tag_button)
        library_widget = QtWidgets.QWidget(self)
        library_widget.setLayout(library_layout)
        self._library_dock = QtWidgets.QDockWidget("Game Library", self)
        self._library_dock.setObjectName("libraryDock")
        self._library_dock.setWidget(library_widget)
        self._library_dock.setTitleBarWidget(DockTitleBar(self._library_dock))

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
        model_center_action = settings_menu.addAction("AI Model Center…")
        model_center_action.triggered.connect(self._open_model_center)

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

        self._workspace_stack = QtWidgets.QStackedWidget(self)
        self._workspace_stack.addWidget(self._board)
        self._qml_workspace = QQuickWidget(self)
        self._qml_workspace.rootContext().setContextProperty("gameController", self._controller)
        self._qml_workspace.rootContext().setContextProperty("uiTheme", self._ui_theme)
        self._qml_workspace.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        self._qml_workspace.setSource(QtCore.QUrl.fromLocalFile(
            str(Path(__file__).resolve().parents[1] / "qml" / "BoardWorkspace.qml")
        ))
        self._workspace_stack.addWidget(self._qml_workspace)
        central_widget = QtWidgets.QWidget(self)
        central_layout = QtWidgets.QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addWidget(self._workspace_stack, 1)
        self.setCentralWidget(central_widget)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._tree_dock)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._analysis_dock)
        self.tabifyDockWidget(self._tree_dock, self._analysis_dock)
        self._analysis_dock.hide()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self._controls_dock)
        view_menu = self.menuBar().addMenu("View")
        qml_action = view_menu.addAction("QML workspace preview")
        qml_action.setCheckable(True)
        qml_action.toggled.connect(lambda enabled: self._workspace_stack.setCurrentIndex(1 if enabled else 0))
        if self._qml_workspace.status() == QQuickWidget.Status.Error:
            errors = "; ".join(error.toString() for error in self._qml_workspace.errors())
            logger.error("QML workspace failed to load: %s", errors)
            qml_action.setEnabled(False)
            self.statusBar().showMessage("QML workspace failed to load; see application log", 8000)
        view_menu.addAction(self._tree_dock.toggleViewAction())
        view_menu.addAction(self._analysis_dock.toggleViewAction())
        view_menu.addAction(self._comments_dock.toggleViewAction())
        view_menu.addAction(self._library_dock.toggleViewAction())
        view_menu.addAction(self._controls_dock.toggleViewAction())
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._comments_dock)
        self.tabifyDockWidget(self._tree_dock, self._comments_dock)
        self._comments_dock.hide()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self._library_dock)
        self.tabifyDockWidget(self._tree_dock, self._library_dock)
        self._library_dock.hide()
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
        self._recovery_path = Path(QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.StandardLocation.AppDataLocation
        )) / "recovery.sgf"
        self._recovery_timer = QtCore.QTimer(self)
        self._recovery_timer.setSingleShot(True)
        self._recovery_timer.setInterval(1200)
        self._recovery_timer.timeout.connect(self._write_recovery)
        self._controller.stateChanged.connect(self._schedule_recovery)
        self._offer_recovery()
        self._refresh_library()
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
        if not self._confirm_discard_changes():
            return
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
        if not self._confirm_discard_changes():
            return
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open SGF", "", "SGF files (*.sgf *.SGF);;All files (*)"
        )
        if not path:
            return
        if self._controller.load_sgf(path):
            self._library.touch(path)
            self._refresh_library()
        if self._controller.current_path == path and len(self._controller.collection.games) > 1:
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
            self._library.touch(path)
            self._refresh_library()
            self._remove_recovery()
            self.statusBar().showMessage(f"Saved {path}", 3000)

    def _confirm_discard_changes(self) -> bool:
        if not self._controller.isDirty:
            return True
        box = QtWidgets.QMessageBox(self)
        box.setWindowTitle("Unsaved game")
        box.setText("This game has unsaved changes.")
        box.setInformativeText("Save the changes before continuing?")
        save = box.addButton(QtWidgets.QMessageBox.StandardButton.Save)
        discard = box.addButton(QtWidgets.QMessageBox.StandardButton.Discard)
        box.addButton(QtWidgets.QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(save)
        box.exec()
        if box.clickedButton() is save:
            self._save_sgf()
            return not self._controller.isDirty
        return box.clickedButton() is discard

    def _offer_recovery(self) -> None:
        if not self._recovery_path.is_file():
            return
        answer = QtWidgets.QMessageBox.question(
            self,
            "Recover unsaved game?",
            "A recent autosaved game was found. Restore it?",
            QtWidgets.QMessageBox.StandardButton.Restore
            | QtWidgets.QMessageBox.StandardButton.Discard,
            QtWidgets.QMessageBox.StandardButton.Restore,
        )
        if answer == QtWidgets.QMessageBox.StandardButton.Restore:
            self._controller.load_recovery(self._recovery_path)
            self.statusBar().showMessage("Recovered autosaved game; save it to keep the changes", 6000)
        else:
            self._remove_recovery()

    def _schedule_recovery(self) -> None:
        if self._controller.isDirty:
            self._recovery_timer.start()
        else:
            self._recovery_timer.stop()
            self._remove_recovery()

    def _write_recovery(self) -> None:
        if not self._controller.isDirty:
            return
        try:
            self._recovery_path.parent.mkdir(parents=True, exist_ok=True)
            self._controller.save_recovery(self._recovery_path)
        except OSError:
            logger.exception("Could not write game recovery snapshot")

    def _remove_recovery(self) -> None:
        try:
            self._recovery_path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Could not remove recovery snapshot %s", self._recovery_path)

    def _refresh_library(self, *_args) -> None:
        if not hasattr(self, "_library_list"):
            return
        self._library_list.clear()
        for path in self._library.search(self._library_search.text()):
            name = Path(path).name
            tags = self._library.tags(path)
            item = QtWidgets.QListWidgetItem(name + ("  ·  " + ", ".join(tags) if tags else ""))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, path)
            self._library_list.addItem(item)

    def _open_library_item(self, item: QtWidgets.QListWidgetItem) -> None:
        if not self._confirm_discard_changes():
            return
        path = str(item.data(QtCore.Qt.ItemDataRole.UserRole))
        if self._controller.load_sgf(path):
            self._library.touch(path)
            self._refresh_library()

    def _edit_library_tags(self) -> None:
        item = self._library_list.currentItem()
        path = str(item.data(QtCore.Qt.ItemDataRole.UserRole)) if item else self._controller.current_path
        if not path:
            self.statusBar().showMessage("Save this game before adding it to the library", 4000)
            return
        tags, accepted = QtWidgets.QInputDialog.getText(
            self, "Game tags", "Comma separated tags", text=", ".join(self._library.tags(path))
        )
        if accepted:
            self._library.set_tags(path, tags.split(","))
            self._refresh_library()

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
            arguments = list(shlex.split(self._settings.value("engine_arguments", "gtp")))
        except ValueError as error:
            self.statusBar().showMessage(f"Invalid engine arguments: {error}", 6000)
            return
        selected_model = str(self._settings.value("engine_model", ""))
        arguments = apply_model_argument(arguments, selected_model)
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

    def _root_info_updated(self, root: AnalysisRoot) -> None:
        if root.winrate is None:
            return
        perspective = (
            self._review_positions[self._review_index][1]
            if self._reviewing and self._review_index < len(self._review_positions)
            else self.game.to_play
        )
        black_winrate = root.winrate if perspective == BLACK else 1.0 - root.winrate
        score = "—" if root.score_lead is None else f"{root.score_lead:+.1f} pts"
        self._analysis_summary.setText(
            f"Position · Black {black_winrate * 100:.1f}% · {score} · {root.visits:,} visits"
        )
        if self._reviewing and self._review_index < len(self._review_positions):
            move_number = self._review_index
            if not self._review_results or self._review_results[-1][0] != move_number:
                self._review_results.append((move_number, black_winrate))
            else:
                self._review_results[-1] = (move_number, black_winrate)
            self._analysis_graph.set_points(self._review_results)

    def _ownership_updated(self, values: tuple[float, ...]) -> None:
        self._latest_ownership = values
        if self._show_ownership.isChecked():
            self._board.set_ownership(values, self.game.size)

    def _start_game_review(self) -> None:
        if self._engine.status != GtpEngine.READY:
            self._analysis_status.setText("Start KataGo before reviewing the game")
            if not self._engine.is_running:
                self._start_engine_analysis()
            return
        session = SgfGameSession(self._controller.root)
        positions = []
        while True:
            positions.append((tuple(tuple(row) for row in session.game.board), session.game.to_play, len(session.path) - 1, session.current_node))
            if not session.can_advance:
                break
            session.next(0)
        self._review_positions = positions
        self._review_results = []
        self._review_index = 0
        self._reviewing = True
        self._review_findings.clear()
        self._analysis_graph.set_points([])
        self._review_stop_button.setEnabled(True)
        self._analysis_status.setText(f"Reviewing {len(positions)} positions…")
        self._review_next_position()

    def _review_next_position(self) -> None:
        if not self._reviewing or self._review_index >= len(self._review_positions):
            self._finish_game_review()
            return
        board, to_play, move_number, _node = self._review_positions[self._review_index]
        try:
            komi = float((self._controller.root.values("KM") or ["6.5"])[0])
        except ValueError:
            komi = 6.5
        self._engine.set_position(self.game.size, komi)
        black, white = [], []
        columns = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        for y, row in enumerate(board):
            for x, color in enumerate(row):
                if color:
                    vertex = f"{columns[x]}{self.game.size - y}"
                    (black if color == BLACK else white).append(vertex)
        self._review_stones_command = self._engine.set_stones(tuple(black), tuple(white))
        self._review_timer.stop()
        self._analysis_status.setText(f"Reviewing move {move_number} ({self._review_index + 1}/{len(self._review_positions)})…")

    def _engine_response_received(self, command_id: int, command: str, _body: str) -> None:
        if self._reviewing and self._review_stones_command is not None and command_id == self._review_stones_command:
            # The final setup response means the engine has the requested board.
            self._review_stones_command = None
            player = "B" if self._review_positions[self._review_index][1] == BLACK else "W"
            QtCore.QTimer.singleShot(0, lambda: self._begin_review_sample(player))
        elif self._reviewing and command == "stop":
            self._review_waiting_analysis_response = False
            self._review_index += 1
            QtCore.QTimer.singleShot(0, self._review_next_position)
        elif self._reviewing and command.startswith("kata-analyze ") and self._review_waiting_analysis_response:
            self._review_waiting_analysis_response = False
            self._review_timer.stop()
            self._review_index += 1
            QtCore.QTimer.singleShot(0, self._review_next_position)

    def _begin_review_sample(self, player: str) -> None:
        if self._reviewing and self._engine.status == GtpEngine.READY:
            self._review_waiting_analysis_response = True
            self._engine.start_analysis(player, interval_ms=500)
            self._review_timer.start()

    def _stop_review_sample(self) -> None:
        if self._reviewing and self._engine.status == GtpEngine.ANALYZING:
            self._engine.stop_analysis()

    def _stop_game_review(self) -> None:
        self._reviewing = False
        self._review_timer.stop()
        self._review_stop_button.setEnabled(False)
        if self._engine.status == GtpEngine.ANALYZING:
            self._engine.stop_analysis()
        self._analysis_status.setText("Review stopped")

    def _finish_game_review(self) -> None:
        self._reviewing = False
        self._review_timer.stop()
        self._review_stop_button.setEnabled(False)
        drops = []
        for previous, current in zip(self._review_results, self._review_results[1:]):
            mover = self._review_positions[current[0]][1]
            loss = previous[1] - current[1] if mover == WHITE else current[1] - previous[1]
            if loss >= 0.08:
                drops.append((loss, current[0]))
        for loss, move in sorted(drops, reverse=True)[:12]:
            mover = "White" if self._review_positions[move][1] == BLACK else "Black"
            item = QtWidgets.QListWidgetItem(f"Move {move} · {mover}: estimated loss {loss * 100:.1f}%")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, move)
            self._review_findings.addItem(item)
        self._analysis_status.setText(f"Review complete · {len(self._review_results)} positions · {len(drops)} major swings")

    def _jump_to_review_move(self, item: QtWidgets.QListWidgetItem) -> None:
        move_number = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(move_number, int):
            self._controller.navigate_to(self._review_positions[move_number][3])

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
        if not self._confirm_discard_changes():
            event.ignore()
            return
        self._recovery_timer.stop()
        self._remove_recovery()
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
        animations_enabled = QtWidgets.QCheckBox(dialog)
        animations_enabled.setChecked(self._settings.value("animations_enabled", True, type=bool))
        theme_selector = QtWidgets.QComboBox(dialog)
        theme_selector.addItems(("Dark", "Warm light"))
        theme_selector.setCurrentText(self._ui_theme)

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
        form.addRow("Application theme", theme_selector)
        form.addRow("Animated board backgrounds", animations_enabled)
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
        theme = theme_selector.currentText()
        enable_animations = animations_enabled.isChecked()
        selected_sound = sound_selector.currentText()
        selected_board = board_selector.currentText()
        selected_stones = stone_selector.currentText()
        selected_engine = engine_program.text().strip()
        selected_arguments = engine_arguments.text().strip()
        self._settings.setValue("font_size", size)
        self._settings.setValue("ui_theme", theme)
        self._settings.setValue("animations_enabled", enable_animations)
        self._settings.setValue("placement_sound", selected_sound)
        self._settings.setValue("board_material", selected_board)
        self._settings.setValue("stone_material", selected_stones)
        self._settings.setValue("engine_program", selected_engine)
        self._settings.setValue("engine_arguments", selected_arguments)
        self._stone_sound.set_sound(selected_sound)
        self._board.set_board_material(selected_board)
        self._board.set_animations_enabled(enable_animations)
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
        self._apply_theme(theme)
        self._qml_workspace.rootContext().setContextProperty("uiTheme", theme)

    def _open_model_center(self) -> None:
        dialog = ModelCenterDialog(self._settings, self)
        dialog.modelSelected.connect(self._model_selected)
        dialog.exec()

    def _model_selected(self, path: str) -> None:
        if self._engine.is_running:
            self._analysis_requested = False
            self._engine.stop()
        self._analysis_status.setText(
            f"Model selected: {Path(path).name}. Start analysis to load it into KataGo."
        )

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

    def _apply_theme(self, theme: str) -> None:
        """Apply a high-contrast application palette and keyboard focus style."""
        light = theme == "Warm light"
        if light:
            background, panel, text, muted = "#f3f0e9", "#fffdf8", "#292d34", "#68717d"
            border, accent, hover = "#ded8ca", "#087e76", "#e8f2ee"
        else:
            background, panel, text, muted = "#111722", "#1b2433", "#e7edf6", "#9aa8bc"
            border, accent, hover = "#303c4e", "#47d8c2", "#273548"
        app = QtWidgets.QApplication.instance()
        if app is None:
            return
        app.setStyle("Fusion")
        palette = app.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(background))
        palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(text))
        palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(panel))
        palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(background))
        palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(text))
        palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(panel))
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(text))
        palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(accent))
        palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor("#101820"))
        app.setPalette(palette)
        app.setStyleSheet(f"""
            QMainWindow, QDialog {{ background: {background}; color: {text}; }}
            QMenuBar, QMenu {{ background: {panel}; color: {text}; border: 1px solid {border}; }}
            QMenu::item:selected, QMenuBar::item:selected {{ background: {hover}; }}
            QDockWidget {{ color: {text}; }}
            QDockWidget::title {{ background: {panel}; padding: 9px 12px; border-bottom: 1px solid {border}; }}
            QPushButton, QToolButton {{ background: {panel}; color: {text}; border: 1px solid {border}; border-radius: 8px; min-height: 34px; padding: 3px 12px; }}
            QPushButton:hover, QToolButton:hover {{ background: {hover}; border-color: {accent}; }}
            QPushButton:pressed {{ background: {accent}; color: #101820; }}
            QPushButton:disabled {{ color: {muted}; }}
            QLineEdit, QPlainTextEdit, QListWidget, QTreeView, QComboBox, QSpinBox {{ background: {panel}; color: {text}; border: 1px solid {border}; border-radius: 6px; padding: 5px; selection-background-color: {accent}; }}
            QComboBox QAbstractItemView {{ background: {panel}; color: {text}; selection-background-color: {accent}; }}
            QCheckBox {{ spacing: 8px; }}
            QWidget:focus {{ outline: 2px solid {accent}; outline-offset: 1px; }}
            QStatusBar {{ color: {muted}; }}
            QScrollBar:vertical {{ background: {background}; width: 12px; margin: 0; }}
            QScrollBar::handle:vertical {{ background: {border}; border-radius: 5px; min-height: 28px; }}
        """)

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
        self.setWindowTitle("NightyGo" + (" *" if self._controller.isDirty else ""))
        if self._engine.status == GtpEngine.ANALYZING:
            self._analysis_requested = False
            self._engine.stop_analysis()
        self._analysis_data.clear()
        self._candidate_list.clear()
        self._analysis_summary.setText("Analysis not available for this move")
        self._board.set_analysis_moves([], self.game.size)
        self._latest_ownership = ()
        self._board.set_ownership((), 0)
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
