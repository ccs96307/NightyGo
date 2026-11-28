"""Main NightyGo application window."""

import logging
import shlex
import subprocess
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtQuickWidgets import QQuickWidget

from nightygo.audio import StoneCaptureSound, StonePlacementSound
from nightygo.engine import AnalysisMove, AnalysisRoot, EngineConfig, GtpEngine
from nightygo.game_controller import GameController
from nightygo.i18n import LANGUAGES, retranslate_widget_tree, translate
from nightygo.library import GameLibrary
from nightygo.materials import STONE_MATERIALS
from nightygo.model import BLACK, WHITE
from nightygo.model_center import (
    ModelCenterDialog,
    apply_config_argument,
    apply_model_argument,
    ensure_gtp_config,
    prepare_gtp_engine,
)
from nightygo.preview import stone_pixmap
from nightygo.sgf_session import SgfGameSession
from nightygo.ui.analysis_graph import AnalysisGraph
from nightygo.ui.board_widget import BoardWidget
from nightygo.ui.dock_title_bar import DockTitleBar
from nightygo.ui.game_tree_view import GameTreeView
from nightygo.ui.theme import apply_application_theme

logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    """Coordinate the Go model and board view."""

    def __init__(self) -> None:
        super().__init__()
        self._settings = QtCore.QSettings("NightyGo", "NightyGo")
        self._language = str(self._settings.value("language", "en"))
        if self._language not in LANGUAGES:
            self._language = "en"
        self._library = GameLibrary(self._settings)
        self._font_size = int(self._settings.value("font_size", 14))
        self._ui_theme = str(self._settings.value("ui_theme", "Dark"))
        self._motion_level = str(self._settings.value("motion_level", ""))
        if self._motion_level not in ("off", "subtle", "full"):
            self._motion_level = (
                "full"
                if self._settings.value("animations_enabled", True, type=bool)
                else "off"
            )
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
        self._engine.outputReceived.connect(self._engine_output_received)
        self._engine.analysisUpdated.connect(self._analysis_updated)
        self._engine.rootInfoUpdated.connect(self._root_info_updated)
        self._engine.ownershipUpdated.connect(self._ownership_updated)
        self._engine.responseReceived.connect(self._engine_response_received)
        self.game = self._controller.game
        self._stone_sound = StonePlacementSound(self)
        self._capture_sound = StoneCaptureSound(self)
        self._discard_on_close = False
        self._engine_shutdown_waiting = False
        self._board = BoardWidget(self)
        self._board.set_ui_theme(self._ui_theme)
        self._board.set_board_material(self._settings.value("board_material", "Classic wood"))
        self._board.set_stone_material(self._settings.value("stone_material", "Traditional"))
        self._board.set_material_strength(int(self._settings.value("material_strength", 100)))
        self._board.set_performance_overlay(self._settings.value("show_performance", False, type=bool))
        self._board.set_motion_level(self._motion_level)
        self._board.set_game(self.game)
        self._board.point_clicked.connect(self._play_at)

        self._undo_button = QtWidgets.QPushButton("Undo")
        self._undo_button.clicked.connect(self._undo)
        self._redo_button = QtWidgets.QPushButton("Redo")
        self._redo_button.clicked.connect(self._redo)
        self._previous_button = QtWidgets.QPushButton("Previous")
        self._previous_button.clicked.connect(self._previous)
        self._next_button = QtWidgets.QPushButton("Next")
        self._next_button.setProperty("variant", "primary")
        self._next_button.clicked.connect(self._next)
        self._variations = QtWidgets.QComboBox()
        self._variations.setMinimumWidth(120)
        self._variations.currentIndexChanged.connect(self._refresh_navigation)
        pass_button = QtWidgets.QPushButton("Pass")
        pass_button.setProperty("variant", "secondary")
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
        self._game_tree.set_motion_level(self._motion_level)

        self._analysis_status = QtWidgets.QLabel(self._t("Open AI Studio and set up a model first"))
        self._analysis_summary = QtWidgets.QLabel("No analysis available")
        self._analysis_summary.setWordWrap(True)
        self._candidate_list = QtWidgets.QListWidget()
        self._candidate_list.itemDoubleClicked.connect(self._play_selected_candidate)
        self._analysis_data: dict[str, AnalysisMove] = {}
        self._last_root_metrics: tuple[float, float | None, int] | None = None
        self._review_drops: list[tuple[float, int]] = []
        self._analysis_requested = False
        self._analysis_restart_pending = False
        self._analysis_position = None
        self._review_positions: list[tuple[tuple[tuple[int, ...], ...], int, int, object]] = []
        self._review_results: list[tuple[int, float]] = []
        self._review_stones_command: int | None = None
        self._review_waiting_analysis_response = False
        self._reviewing = False
        self._review_requested = False
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
        self._analysis_graph.move_selected.connect(self._jump_to_review_move)
        review_button = QtWidgets.QPushButton("Review full game")
        review_button.clicked.connect(self._start_game_review)
        self._review_stop_button = QtWidgets.QPushButton("Stop review")
        self._review_stop_button.clicked.connect(self._stop_game_review)
        self._review_stop_button.setEnabled(False)
        self._review_findings = QtWidgets.QListWidget(self)
        self._review_findings.itemClicked.connect(self._jump_to_review_move)
        self._start_analysis_button = QtWidgets.QPushButton("Analyze position")
        self._start_analysis_button.clicked.connect(self._start_analysis_button_clicked)
        stop_analysis_button = QtWidgets.QPushButton("Stop")
        stop_analysis_button.clicked.connect(self._stop_engine_analysis)
        configure_engine_button = QtWidgets.QPushButton("AI Studio…")
        configure_engine_button.setProperty("variant", "secondary")
        configure_engine_button.clicked.connect(self._open_model_center)
        play_candidate_button = QtWidgets.QPushButton("Play selected move")
        play_candidate_button.clicked.connect(self._play_selected_candidate)
        analysis_buttons = QtWidgets.QHBoxLayout()
        analysis_buttons.addWidget(self._start_analysis_button)
        analysis_buttons.addWidget(stop_analysis_button)
        analysis_layout = QtWidgets.QVBoxLayout()
        analysis_layout.addWidget(self._analysis_status)
        analysis_layout.addWidget(self._analysis_summary)
        analysis_layout.addWidget(self._analysis_graph)
        analysis_layout.addWidget(self._show_ownership)
        analysis_layout.addWidget(self._candidate_list, 1)
        analysis_layout.addLayout(analysis_buttons)
        analysis_layout.addWidget(configure_engine_button)
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
        self._library_empty = QtWidgets.QLabel(self._t("No saved games yet"), self)
        self._library_empty.setObjectName("emptyState")
        self._library_empty.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._library_stack = QtWidgets.QStackedWidget(self)
        self._library_stack.addWidget(self._library_empty)
        self._library_stack.addWidget(self._library_list)
        tag_button = QtWidgets.QPushButton("Edit tags…", self)
        tag_button.clicked.connect(self._edit_library_tags)
        library_layout = QtWidgets.QVBoxLayout()
        library_layout.addWidget(self._library_search)
        library_layout.addWidget(self._library_stack, 1)
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
        self._create_edit_menu()
        header_toolbar = self.addToolBar("NightyGo")
        header_toolbar.setObjectName("mainHeaderToolbar")
        header_toolbar.setMovable(False)
        self._brand_label = QtWidgets.QLabel("NIGHTYGO", self)
        self._brand_label.setObjectName("brandMark")
        self._brand_caption = QtWidgets.QLabel(self._t("Go · Study Studio"), self)
        self._brand_caption.setObjectName("brandCaption")
        header_toolbar.addWidget(self._brand_label)
        header_toolbar.addWidget(self._brand_caption)
        header_toolbar.addSeparator()
        header_spacer = QtWidgets.QWidget(self)
        header_spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        header_toolbar.addWidget(header_spacer)
        self._toolbar_status = QtWidgets.QLabel(self)
        self._toolbar_status.setObjectName("toolbarStatus")
        header_toolbar.addWidget(self._toolbar_status)
        header_toolbar.addSeparator()
        self._language_button = QtWidgets.QToolButton(self)
        self._language_button.setObjectName("languageButton")
        self._language_button.setProperty("variant", "quiet")
        self._language_button.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self._language_menu = QtWidgets.QMenu(self._language_button)
        self._language_actions: dict[str, QtGui.QAction] = {}
        language_group = QtGui.QActionGroup(self)
        language_group.setExclusive(True)
        for code, label in LANGUAGES.items():
            action = self._language_menu.addAction(label)
            action.setCheckable(True)
            action.setData(code)
            action.setChecked(code == self._language)
            action.triggered.connect(lambda _checked=False, selected=code: self._set_language(selected))
            language_group.addAction(action)
            self._language_actions[code] = action
        self._language_button.setMenu(self._language_menu)
        header_toolbar.addWidget(self._language_button)
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
        controls_widget.setObjectName("controlsSurface")
        controls_widget.setLayout(controls)
        controls.setContentsMargins(14, 8, 14, 8)
        controls.setSpacing(8)
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
        self._qml_workspace.rootContext().setContextProperty("uiLanguage", self._language)
        self._qml_workspace.rootContext().setContextProperty("uiFontSize", self._font_size)
        self._qml_workspace.rootContext().setContextProperty(
            "boardMaterialName", self._settings.value("board_material", "Classic wood")
        )
        self._qml_workspace.rootContext().setContextProperty(
            "stoneMaterialName", self._settings.value("stone_material", "Traditional")
        )
        self._qml_workspace.rootContext().setContextProperty("motionLevel", self._motion_level)
        self._qml_workspace.rootContext().setContextProperty(
            "materialStrength", int(self._settings.value("material_strength", 100)) / 100.0
        )
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
        view_menu.addSeparator()
        for label, preset in (("Play layout", "play"), ("Review layout", "review"), ("Study layout", "study")):
            action = view_menu.addAction(label)
            action.triggered.connect(lambda _checked=False, name=preset: self._apply_layout_preset(name))
        settings_menu = self.menuBar().addMenu("Settings")
        preferences_action = settings_menu.addAction("Preferences…")
        preferences_action.triggered.connect(self._open_settings)
        model_center_action = settings_menu.addAction("AI Studio…")
        model_center_action.triggered.connect(self._open_model_center)
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
        self._retranslate_ui()

    def _t(self, source: str, **values) -> str:
        return translate(source, self._language, **values)

    def _set_language(self, language: str) -> None:
        if language not in LANGUAGES or language == self._language:
            return
        self._language = language
        self._settings.setValue("language", language)
        self._settings.sync()
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        retranslate_widget_tree(self, self._language)
        for code, action in self._language_actions.items():
            action.setChecked(code == self._language)
        self._language_button.setText(self._t("Language"))
        self._language_button.setToolTip(self._t("Language"))
        self._brand_caption.setText(self._t("Go · Study Studio"))
        if self._library_list.count() == 0:
            self._library_empty.setText(
                self._t("No games match this search" if self._library_search.text().strip() else "No saved games yet")
            )
        for dock in (self._tree_dock, self._analysis_dock, self._comments_dock, self._library_dock, self._controls_dock):
            title_bar = dock.titleBarWidget()
            if isinstance(title_bar, DockTitleBar):
                title_bar.set_language(self._language)
        self._game_tree.set_language(self._language)
        self._game_tree.set_theme(self._ui_theme)
        self._analysis_graph.set_language(self._language)
        self._analysis_graph.set_theme(self._ui_theme)
        self._qml_workspace.rootContext().setContextProperty("uiLanguage", self._language)
        self.setWindowTitle("NightyGo" + (" *" if self._controller.isDirty else ""))
        self._capture_label.setText(
            self._t("Captured  Black: {black}   White: {white}", black=self.game.captures[BLACK], white=self.game.captures[WHITE])
        )
        if self.game.is_finished:
            self.statusBar().showMessage(self._t("Game ended after two passes"))
            self._toolbar_status.setText(self._t("Game ended after two passes"))
        else:
            color = self._t("Black" if self.game.to_play == BLACK else "White")
            self.statusBar().showMessage(self._t("{color} to play", color=color))
            self._toolbar_status.setText(self._t("{color} to play", color=color))
        self._populate_variations(self._variations.currentIndex())
        if self._analysis_data:
            for candidate in tuple(self._analysis_data.values()):
                self._analysis_updated(candidate)
        if self._last_root_metrics is not None:
            self._set_root_summary(*self._last_root_metrics)
        elif not self._review_results:
            self._analysis_summary.setText(self._t("Analysis not available for this move"))
        self._review_findings.clear()
        for loss, move in getattr(self, "_review_drops", []):
            mover = "White" if self._review_positions[move][1] == BLACK else "Black"
            item = QtWidgets.QListWidgetItem(self._t("Move {number} · {color}: estimated loss {loss:.1f}%", number=move, color=self._t(mover), loss=loss * 100))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, move)
            self._review_findings.addItem(item)
        if self._reviewing:
            self._analysis_status.setText(self._t("Reviewing {count} positions…", count=len(self._review_positions)))
        elif self._engine.status in (GtpEngine.STARTING, GtpEngine.STOPPED, GtpEngine.ANALYZING, GtpEngine.ERROR):
            self._engine_status_changed(self._engine.status)
        else:
            self._analysis_status.setText(self._t("Engine ready"))

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
            self._play_move_sounds()

    def _play_move_sounds(self) -> None:
        self._stone_sound.play()
        move = self.game.last_move
        if move is not None and move.captured:
            captured_count = len(move.captured)
            QtCore.QTimer.singleShot(90, lambda count=captured_count: self._capture_sound.play(count))

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
            self._t("New Game"),
            self._t("Board size"),
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
            self, self._t("Open SGF…"), "", self._t("SGF files (*.sgf *.SGF);;All files (*)")
        )
        if not path:
            return
        if self._controller.load_sgf(path):
            self._library.touch(path)
            self._refresh_library()
        if self._controller.current_path == path and len(self._controller.collection.games) > 1:
            self.statusBar().showMessage(
                self._t("Loaded the first game; all game trees are preserved when saving"),
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
            self._t("Save SGF"),
            self._controller.current_path or "game.sgf",
            self._t("SGF files (*.sgf)"),
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
            self.statusBar().showMessage(self._t("Saved {path}", path=path), 3000)

    def _confirm_discard_changes(self) -> bool:
        if not self._controller.isDirty:
            return True
        box = QtWidgets.QMessageBox(self)
        box.setWindowTitle(self._t("Unsaved game"))
        box.setText(self._t("This game has unsaved changes."))
        box.setInformativeText(self._t("Save the changes before continuing?"))
        save = box.addButton(self._t("Save"), QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        discard = box.addButton(self._t("Discard"), QtWidgets.QMessageBox.ButtonRole.DestructiveRole)
        box.addButton(self._t("Cancel"), QtWidgets.QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(save)
        box.exec()
        if box.clickedButton() is save:
            self._save_sgf()
            return not self._controller.isDirty
        return box.clickedButton() is discard

    def _offer_recovery(self) -> None:
        if not self._recovery_path.is_file():
            return
        box = QtWidgets.QMessageBox(self)
        box.setWindowTitle(self._t("Recover unsaved game?"))
        box.setText(self._t("A recent autosaved game was found. Restore it?"))
        restore = box.addButton(self._t("Restore"), QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        box.addButton(self._t("Discard"), QtWidgets.QMessageBox.ButtonRole.DestructiveRole)
        box.setDefaultButton(restore)
        box.exec()
        if box.clickedButton() is restore:
            self._controller.load_recovery(self._recovery_path)
            self.statusBar().showMessage(self._t("Recovered autosaved game; save it to keep the changes"), 6000)
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
        has_results = self._library_list.count() > 0
        if not has_results:
            self._library_empty.setText(
                self._t("No games match this search" if self._library_search.text().strip() else "No saved games yet")
            )
        self._library_stack.setCurrentWidget(self._library_list if has_results else self._library_empty)

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
            self.statusBar().showMessage(self._t("Save game before adding it to the library"), 4000)
            return
        tags, accepted = QtWidgets.QInputDialog.getText(
            self, self._t("Game tags"), self._t("Comma separated tags"), text=", ".join(self._library.tags(path))
        )
        if accepted:
            self._library.set_tags(path, tags.split(","))
            self._refresh_library()

    def _save_current_comment(self) -> None:
        self._controller.set_current_comment(self._comment_editor.toPlainText())
        self.statusBar().showMessage(self._t("Comment saved to the current SGF node"), 3000)

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
        dialog.setWindowTitle(self._t("Game information"))
        inputs: dict[str, QtWidgets.QLineEdit] = {}
        form = QtWidgets.QFormLayout()
        for identifier, label in fields:
            field = QtWidgets.QLineEdit(
                (self._controller.root.values(identifier) or [""])[0], dialog
            )
            inputs[identifier] = field
            form.addRow(self._t(label), field)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText(self._t("OK"))
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setText(self._t("Cancel"))
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
        action = "two intersections" if mode in ("line", "arrow") else "one intersection"
        self.statusBar().showMessage(self._t("Click {target} on the board to add markup", target=self._t(action)), 5000)

    def _apply_markup(self, x: int, y: int, mode: str) -> None:
        if mode in ("line", "arrow"):
            if self._pending_line_start is None:
                self._pending_line_start = (x, y)
                self.statusBar().showMessage(self._t("Select the end point"), 5000)
                return
            x1, y1 = self._pending_line_start
            self._pending_line_start = None
            self._board.set_markup_mode("")
            self._controller.add_line_markup(mode, x1, y1, x, y)
            return
        label = ""
        if mode == "label":
            label, accepted = QtWidgets.QInputDialog.getText(
                self, self._t("Text label…"), self._t("Label text")
            )
            if not accepted or not label:
                return
        self._controller.add_markup(mode, x, y, label)

    def _start_engine_analysis(self) -> None:
        self._analysis_dock.show()
        if self._engine.status == GtpEngine.ANALYZING:
            self._review_requested = False
            self._analysis_requested = False
            self._engine.stop_analysis()
            self._analysis_status.setText(self._t("Stopping analysis…"))
            return
        if self._engine.status == GtpEngine.READY:
            self._request_current_position_analysis()
            return
        if self._engine.status == GtpEngine.STARTING and self._engine.is_running:
            self._analysis_requested = True
            self._analysis_status.setText(self._t("Starting KataGo…"))
            return
        configured_program = str(self._settings.value("engine_program", ""))
        if not configured_program:
            self._analysis_requested = False
            self._analysis_status.setText(self._t("Open AI Studio and set up a model first"))
            return
        try:
            program = prepare_gtp_engine(configured_program)
            if not program.is_file():
                raise ValueError(self._t("KataGo executable was not found. Reinstall it in AI Studio."))
            config = Path(str(self._settings.value("engine_config", "")))
            if not config.is_file():
                config = ensure_gtp_config()
            model = Path(str(self._settings.value("engine_model", "")))
            if not model.is_file():
                raise ValueError(self._t("The selected AI model file is missing. Download or choose a model in AI Studio."))
            self._settings.setValue("engine_program", str(program))
            self._settings.setValue("engine_config", str(config))
            self._settings.sync()
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            self._analysis_requested = False
            self._analysis_status.setText(self._t("AI setup needs attention: {error}", error=error))
            self.statusBar().showMessage(str(error), 8000)
            logger.exception("Could not prepare KataGo for analysis")
            return
        try:
            arguments = list(shlex.split(self._settings.value("engine_arguments", "gtp")))
        except ValueError as error:
            self.statusBar().showMessage(self._t("Invalid engine arguments: {error}", error=error), 6000)
            return
        arguments = list(apply_config_argument(arguments, str(config)))
        arguments = list(apply_model_argument(arguments, str(model)))
        self._analysis_requested = not self._review_requested
        self._analysis_status.setText(self._t("Starting KataGo…"))
        logger.info("Starting KataGo for analysis: %s %s", program, arguments)
        self._engine.start(
            EngineConfig(str(program), tuple(arguments), str(config.parent))
        )

    def _start_analysis_button_clicked(self) -> None:
        """Start position analysis and cancel any queued review request."""
        self._review_requested = False
        self._review_stop_button.setEnabled(False)
        self._start_engine_analysis()

    def _stop_engine_analysis(self) -> None:
        self._analysis_restart_pending = False
        self._analysis_requested = False
        self._engine.stop_analysis()

    def _engine_ready(self, name: str, version: str) -> None:
        if self._reviewing:
            return
        self._analysis_status.setText(f"{name} · {version}")
        if self._review_requested:
            self._begin_game_review()
        elif self._analysis_requested:
            self._request_current_position_analysis()

    def _engine_status_changed(self, status: str) -> None:
        if status == GtpEngine.ERROR:
            self._analysis_status.setText(self._t("Engine error; see status message"))
        elif status == GtpEngine.STOPPED and self._analysis_requested:
            QtCore.QTimer.singleShot(0, self._start_engine_analysis)
        elif status == GtpEngine.STARTING:
            self._analysis_status.setText(self._t("Starting engine…"))
        elif status == GtpEngine.STOPPED:
            self._analysis_status.setText(self._t("Engine stopped"))
        elif status == GtpEngine.ANALYZING:
            self._analysis_status.setText(self._t("Analyzing current position…"))
        elif status == GtpEngine.READY and self._review_requested:
            self._begin_game_review()
        elif status == GtpEngine.READY and self._analysis_restart_pending and self._analysis_requested:
            self._request_current_position_analysis()

    def _engine_output_received(self, line: str) -> None:
        if self._engine.status != GtpEngine.STARTING:
            return
        message = line.casefold()
        if "autotun" in message or "opencl device" in message or "finding available gpu" in message:
            self._analysis_status.setText(self._t("Preparing GPU for first use…"))
        elif "neural net" in message or "loading model" in message:
            self._analysis_status.setText(self._t("Loading the selected AI model…"))

    def _request_current_position_analysis(self) -> None:
        self._analysis_requested = True
        self._analysis_restart_pending = False
        self._analysis_position = self._current_analysis_position()
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
        if self._analysis_restart_pending or not (self._reviewing or self._analysis_requested):
            return
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
                f"{candidate.score_lead:+.1f} {self._t('pts')}"
                if candidate.score_lead is not None
                else "—"
            )
            item = QtWidgets.QListWidgetItem(
                self._t(
                    "{rank}  {vertex} · {winrate} · {score} · {visits} {unit}",
                    rank=candidate.order + 1 if candidate.order is not None else "·",
                    vertex=candidate.vertex,
                    winrate=winrate,
                    score=score,
                    visits=f"{candidate.visits:,}",
                    unit=self._t("Visits"),
                )
            )
            item.setData(QtCore.Qt.ItemDataRole.UserRole, candidate.vertex)
            self._candidate_list.addItem(item)
        if ordered:
            best = ordered[0]
            winrate = "—" if best.winrate is None else f"{best.winrate * 100:.1f}%"
            score = "—" if best.score_lead is None else f"{best.score_lead:+.1f} {self._t('pts')}"
            self._analysis_summary.setText(
                self._t("Top move {vertex} · {winrate} · {score} · {visits} visits", vertex=best.vertex, winrate=winrate, score=score, visits=f"{best.visits:,}")
            )
        self._board.set_analysis_moves(
            [candidate.vertex for candidate in ordered[:8]],
            self.game.size,
        )

    def _root_info_updated(self, root: AnalysisRoot) -> None:
        if self._analysis_restart_pending or not (self._reviewing or self._analysis_requested):
            return
        if root.winrate is None:
            return
        perspective = (
            self._review_positions[self._review_index][1]
            if self._reviewing and self._review_index < len(self._review_positions)
            else self.game.to_play
        )
        black_winrate = root.winrate if perspective == BLACK else 1.0 - root.winrate
        score = root.score_lead
        if perspective == WHITE and score is not None:
            score = -score
        self._last_root_metrics = (black_winrate, score, root.visits)
        self._set_root_summary(*self._last_root_metrics)

        if self._reviewing and self._review_index < len(self._review_positions):
            move_number = self._review_index
            if not self._review_results or self._review_results[-1][0] != move_number:
                self._review_results.append((move_number, black_winrate))
            else:
                self._review_results[-1] = (move_number, black_winrate)
            self._analysis_graph.set_points(self._review_results)
            self._analysis_graph.set_current_move(move_number)

    def _set_root_summary(self, black_winrate: float, score_lead: float | None, visits: int) -> None:
        score = "—" if score_lead is None else f"{score_lead:+.1f} {self._t('pts')}"
        self._analysis_summary.setText(
            self._t("Position · Black {winrate} · {score} · {visits} visits", winrate=f"{black_winrate * 100:.1f}%", score=score, visits=f"{visits:,}")
        )

    def _ownership_updated(self, values: tuple[float, ...]) -> None:
        if self._analysis_restart_pending or not (self._reviewing or self._analysis_requested):
            return
        self._latest_ownership = values
        if self._show_ownership.isChecked():
            self._board.set_ownership(values, self.game.size)

    def _start_game_review(self) -> None:
        self._analysis_dock.show()
        if not self._settings.value("engine_program", ""):
            self._review_requested = False
            self._review_stop_button.setEnabled(False)
            self._analysis_status.setText(self._t("Open AI Studio and set up a model first"))
            return
        if self._engine.status != GtpEngine.READY:
            self._review_requested = True
            self._analysis_requested = False
            self._review_stop_button.setEnabled(True)
            self._analysis_status.setText(self._t("Starting KataGo…"))
            if self._engine.status == GtpEngine.ANALYZING:
                self._engine.stop_analysis()
                return
            if not self._engine.is_running:
                self._start_engine_analysis()
            return
        self._begin_game_review()

    def _begin_game_review(self) -> None:
        self._analysis_restart_pending = False
        self._analysis_requested = False
        if not self._review_requested and self._engine.status != GtpEngine.READY:
            return
        self._review_requested = False
        self._review_stop_button.setEnabled(True)
        self._start_analysis_button.setEnabled(False)
        session = SgfGameSession(self._controller.root)
        positions = []
        while True:
            positions.append((tuple(tuple(row) for row in session.game.board), session.game.to_play, len(session.path) - 1, session.current_node))
            if not session.can_advance:
                break
            session.next(0)
        self._review_positions = positions
        self._review_results = []
        self._review_drops = []
        self._review_index = 0
        self._reviewing = True
        self._review_findings.clear()
        self._analysis_graph.set_points([])
        self._analysis_graph.set_current_move(None)
        self._review_stop_button.setEnabled(True)
        self._analysis_status.setText(self._t("Reviewing {count} positions…", count=len(positions)))
        self._review_next_position()

    def _review_next_position(self) -> None:
        if not self._reviewing or self._review_index >= len(self._review_positions):
            self._finish_game_review()
            return
        board, _to_play, move_number, _node = self._review_positions[self._review_index]
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
        self._analysis_status.setText(self._t("Reviewing move {number} ({current}/{total})…", number=move_number, current=self._review_index + 1, total=len(self._review_positions)))

    def _engine_response_received(self, command_id: int, command: str, _body: str) -> None:
        if self._reviewing and self._review_stones_command is not None and command_id == self._review_stones_command:
            # The final setup response means the engine has the requested board.
            self._review_stones_command = None
            player = "B" if self._review_positions[self._review_index][1] == BLACK else "W"
            QtCore.QTimer.singleShot(0, lambda: self._begin_review_sample(player))
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
        self._review_requested = False
        self._reviewing = False
        self._review_timer.stop()
        self._review_stop_button.setEnabled(False)
        self._start_analysis_button.setEnabled(True)
        if self._engine.status == GtpEngine.ANALYZING:
            self._engine.stop_analysis()
        self._analysis_status.setText(self._t("Review stopped"))

    def _finish_game_review(self) -> None:
        self._reviewing = False
        self._review_timer.stop()
        self._review_stop_button.setEnabled(False)
        self._start_analysis_button.setEnabled(True)
        drops = []
        for previous, current in zip(self._review_results, self._review_results[1:]):
            mover = self._review_positions[current[0]][1]
            loss = previous[1] - current[1] if mover == WHITE else current[1] - previous[1]
            if loss >= 0.08:
                drops.append((loss, current[0]))
        self._review_drops = sorted(drops, reverse=True)[:12]
        for loss, move in self._review_drops:
            mover = "White" if self._review_positions[move][1] == BLACK else "Black"
            item = QtWidgets.QListWidgetItem(self._t("Move {number} · {color}: estimated loss {loss:.1f}%", number=move, color=self._t(mover), loss=loss * 100))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, move)
            self._review_findings.addItem(item)
        self._analysis_status.setText(self._t("Review complete · {positions} positions · {swings} major swings", positions=len(self._review_results), swings=len(drops)))

    def _jump_to_review_move(self, item: QtWidgets.QListWidgetItem | int) -> None:
        move_number = item if isinstance(item, int) else item.data(QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(move_number, int) and 0 <= move_number < len(self._review_positions):
            self._controller.navigate_to(self._review_positions[move_number][3])

    def _apply_layout_preset(self, preset: str) -> None:
        """Show panels suited to playing, reviewing, or studying."""
        self._tree_dock.show()
        self._comments_dock.setVisible(preset != "play")
        self._analysis_dock.setVisible(preset == "review")
        self._library_dock.setVisible(preset == "study")
        self._controls_dock.show()
        self.statusBar().showMessage(self._t("{name} layout", name=preset.title()), 2500)

    def _play_selected_candidate(self, *_args) -> None:
        item = self._candidate_list.currentItem()
        if item is None:
            return
        vertex = str(item.data(QtCore.Qt.ItemDataRole.UserRole))
        if vertex.casefold() == "pass":
            self._controller.pass_turn()
            return
        columns = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
        if len(vertex) < 2 or vertex[0] not in columns:
            return
        try:
            x = columns.index(vertex[0])
            y = self.game.size - int(vertex[1:])
        except ValueError:
            return
        if self._controller.play_at(x, y):
            self._play_move_sounds()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if not self._discard_on_close:
            if not self._confirm_discard_changes():
                event.ignore()
                return
            self._discard_on_close = True
        if self._engine.is_running:
            event.ignore()
            if not self._engine_shutdown_waiting:
                self._engine_shutdown_waiting = True
                self._analysis_requested = False
                self._review_requested = False
                self._analysis_status.setText(self._t("Stopping KataGo before closing…"))
                self._engine.statusChanged.connect(self._close_after_engine_shutdown)
                self._engine.stop()
            return
        self._recovery_timer.stop()
        self._remove_recovery()
        super().closeEvent(event)

    def _close_after_engine_shutdown(self, status: str) -> None:
        if status not in (GtpEngine.STOPPED, GtpEngine.ERROR) or self._engine.is_running:
            return
        self._engine.statusChanged.disconnect(self._close_after_engine_shutdown)
        QtCore.QTimer.singleShot(0, self.close)

    def _show_error(self, title: str, error: Exception) -> None:
        QtWidgets.QMessageBox.critical(self, title, str(error))

    def _open_settings(self) -> None:
        original = (
            self._font_size,
            self._ui_theme,
            self._motion_level,
            self._stone_sound.selected_sound,
            str(self._settings.value("board_material", "Classic wood")),
            str(self._settings.value("stone_material", "Traditional")),
            int(self._settings.value("material_strength", 100)),
            self._settings.value("show_performance", False, type=bool),
        )
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self._t("NightyGo Preferences"))
        font_size = QtWidgets.QSpinBox(dialog)
        font_size.setRange(10, 30)
        font_size.setSuffix(" pt")
        font_size.setValue(self._font_size)
        motion_selector = QtWidgets.QComboBox(dialog)
        for level, label in (("off", "Off"), ("subtle", "Subtle"), ("full", "Full")):
            motion_selector.addItem(self._t(label), level)
        motion_selector.setCurrentIndex(motion_selector.findData(self._motion_level))
        theme_selector = QtWidgets.QComboBox(dialog)
        for theme in ("Dark", "Warm light", "High contrast"):
            theme_selector.addItem(self._t(theme), theme)
        theme_selector.setCurrentIndex(theme_selector.findData(self._ui_theme))

        sound_selector = QtWidgets.QComboBox(dialog)
        for sound in StonePlacementSound.available_sounds():
            sound_selector.addItem(self._t(sound), sound)
        saved_sound = self._settings.value(
            "placement_sound", StonePlacementSound.available_sounds()[0]
        )
        if saved_sound in StonePlacementSound.available_sounds():
            sound_selector.setCurrentIndex(sound_selector.findData(saved_sound))
        preview_button = QtWidgets.QPushButton(self._t("Preview"), dialog)
        preview_button.clicked.connect(
            lambda: self._stone_sound.play(sound_selector.currentData())
        )
        sound_row = QtWidgets.QHBoxLayout()
        sound_row.addWidget(sound_selector, 1)
        sound_row.addWidget(preview_button)

        board_selector = QtWidgets.QComboBox(dialog)
        for material in BoardWidget.available_board_materials():
            board_selector.addItem(self._t(material), material)
        board_selector.setCurrentIndex(board_selector.findData(
            self._settings.value("board_material", "Classic wood")
        ))
        stone_selector = QtWidgets.QComboBox(dialog)
        for material in STONE_MATERIALS:
            stone_selector.addItem(self._t(material), material)
        stone_selector.setCurrentIndex(stone_selector.findData(
            self._settings.value("stone_material", "Traditional")
        ))
        stone_preview_row = QtWidgets.QHBoxLayout()
        stone_preview_labels = []
        for color, label_text in ((BLACK, self._t("Black")), (WHITE, self._t("White"))):
            preview_label = QtWidgets.QLabel(label_text, dialog)
            preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            preview_label.setMinimumSize(74, 78)
            preview_label.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
            stone_preview_row.addWidget(preview_label)
            stone_preview_labels.append((preview_label, color))

        def update_stone_previews(*_args) -> None:
            material_name = str(stone_selector.currentData() or "Traditional")
            material = STONE_MATERIALS[material_name]
            for preview_label, color in stone_preview_labels:
                pixmap = stone_pixmap(color, material).scaled(
                    54,
                    54,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation,
                )
                preview_label.setPixmap(pixmap)

        stone_selector.currentIndexChanged.connect(update_stone_previews)
        update_stone_previews()
        preset_selector = QtWidgets.QComboBox(dialog)
        for label in ("Custom", "Quiet wood", "Aurora night", "Moonlit study"):
            preset_selector.addItem(self._t(label), label)
        current_board = str(self._settings.value("board_material", "Classic wood"))
        current_stone = str(self._settings.value("stone_material", "Traditional"))
        if current_board == "Classic wood" and current_stone == "Traditional" and self._ui_theme == "Warm light":
            active_preset = "Quiet wood"
        elif current_board == "Starfield" and current_stone == "Starfield":
            active_preset = "Aurora night"
        elif current_board == "Night sky" and current_stone == "Moonstone":
            active_preset = "Moonlit study"
        else:
            active_preset = "Custom"
        preset_selector.setCurrentIndex(preset_selector.findData(active_preset))
        material_strength = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, dialog)
        material_strength.setRange(25, 100)
        material_strength.setValue(original[6])
        performance_overlay = QtWidgets.QCheckBox(self._t("Show board FPS"), dialog)
        performance_overlay.setChecked(original[7])
        form = QtWidgets.QFormLayout()
        form.addRow(self._t("Application font size"), font_size)
        form.addRow(self._t("Application theme"), theme_selector)
        form.addRow(self._t("Motion effects"), motion_selector)
        form.addRow(self._t("Go stone placement sound"), sound_row)
        form.addRow(self._t("Board texture"), board_selector)
        form.addRow(self._t("Stone texture"), stone_selector)
        form.addRow(self._t("Stone preview"), stone_preview_row)
        form.addRow(self._t("Visual preset"), preset_selector)
        form.addRow(self._t("Material strength"), material_strength)
        form.addRow(self._t("Performance"), performance_overlay)
        preview_hint = QtWidgets.QLabel(
            self._t("Changes preview immediately. OK saves them; Cancel restores the previous settings."),
            dialog,
        )
        preview_hint.setWordWrap(True)
        source_hint = QtWidgets.QLabel(self._t("Five real Go-stone recordings from two board types."))
        source_hint.setWordWrap(True)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel,
            parent=dialog,
        )
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText(self._t("OK"))
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel).setText(self._t("Cancel"))
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addLayout(form)
        layout.addWidget(preview_hint)
        layout.addWidget(source_hint)
        layout.addWidget(buttons)

        def apply_selection(*_args) -> None:
            preset = preset_selector.currentData()
            if preset == "Quiet wood":
                theme, board_name, stone_name = "Warm light", "Classic wood", "Traditional"
            elif preset == "Aurora night":
                theme, board_name, stone_name = "Dark", "Starfield", "Starfield"
            elif preset == "Moonlit study":
                theme, board_name, stone_name = "Dark", "Night sky", "Moonstone"
            else:
                theme = board_name = stone_name = None
            if preset != "Custom" and getattr(apply_selection, "preset_applied", None) != preset:
                apply_selection.preset_applied = preset
                theme_selector.setCurrentIndex(theme_selector.findData(theme))
                board_selector.setCurrentIndex(board_selector.findData(board_name))
                stone_selector.setCurrentIndex(stone_selector.findData(stone_name))
            self._apply_preferences_preview(
                font_size.value(),
                theme_selector.currentData() or original[1],
                str(motion_selector.currentData() or original[2]),
                sound_selector.currentData() or original[3],
                board_selector.currentData() or original[4],
                stone_selector.currentData() or original[5],
                material_strength.value(),
                performance_overlay.isChecked(),
            )

        for control, signal in (
            (font_size, font_size.valueChanged),
            (theme_selector, theme_selector.currentIndexChanged),
            (motion_selector, motion_selector.currentIndexChanged),
            (sound_selector, sound_selector.currentIndexChanged),
            (board_selector, board_selector.currentIndexChanged),
            (stone_selector, stone_selector.currentIndexChanged),
            (preset_selector, preset_selector.currentIndexChanged),
            (material_strength, material_strength.valueChanged),
            (performance_overlay, performance_overlay.toggled),
        ):
            signal.connect(apply_selection)
        apply_selection()

        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            self._apply_preferences_preview(*original)
            return

        size = font_size.value()
        theme = theme_selector.currentData()
        selected_motion = str(motion_selector.currentData())
        selected_sound = sound_selector.currentData()
        selected_board = board_selector.currentData()
        selected_stones = stone_selector.currentData()
        selected_strength = material_strength.value()
        show_performance = performance_overlay.isChecked()
        self._settings.setValue("font_size", size)
        self._settings.setValue("ui_theme", theme)
        self._settings.setValue("motion_level", selected_motion)
        self._settings.setValue("animations_enabled", selected_motion != "off")
        self._settings.setValue("placement_sound", selected_sound)
        self._settings.setValue("board_material", selected_board)
        self._settings.setValue("stone_material", selected_stones)
        self._settings.setValue("material_strength", selected_strength)
        self._settings.setValue("show_performance", show_performance)
        self._apply_preferences_preview(
            size, theme, selected_motion, selected_sound, selected_board, selected_stones,
            selected_strength, show_performance
        )
        logger.info(
            "Preferences updated: font=%d pt, board=%s, stones=%s, motion=%s, sound=%s",
            size,
            selected_board,
            selected_stones,
            selected_motion,
            selected_sound,
        )

    def _apply_preferences_preview(
        self,
        size: int,
        theme: str,
        motion: str,
        sound: str,
        board_material: str,
        stone_material: str,
        material_strength: int = 100,
        show_performance: bool = False,
    ) -> None:
        """Apply a live Preferences preview without persisting it."""
        self._set_font_size(size)
        self._apply_theme(theme)
        self._motion_level = motion
        self._stone_sound.set_sound(sound)
        self._board.set_motion_level(motion)
        self._board.set_board_material(board_material)
        self._board.set_stone_material(stone_material)
        self._board.set_material_strength(material_strength)
        self._board.set_performance_overlay(show_performance)
        self._game_tree.set_motion_level(motion)
        self._game_tree.set_stone_material(stone_material)
        self._qml_workspace.rootContext().setContextProperty("uiTheme", theme)
        self._qml_workspace.rootContext().setContextProperty("boardMaterialName", board_material)
        self._qml_workspace.rootContext().setContextProperty("stoneMaterialName", stone_material)
        self._qml_workspace.rootContext().setContextProperty("motionLevel", motion)
        self._qml_workspace.rootContext().setContextProperty(
            "materialStrength", material_strength / 100.0
        )

    def _open_model_center(self) -> None:
        dialog = ModelCenterDialog(self._settings, self)
        dialog.modelSelected.connect(self._model_selected)
        result = dialog.exec()
        if result != QtWidgets.QDialog.DialogCode.Accepted:
            return
        self._analysis_status.setText(self._t("Starting AI analysis…"))

    def _model_selected(self, path: str) -> None:
        logger.info("AI model selected: %s", path)
        self._analysis_requested = True
        self._analysis_status.setText(self._t("Starting AI analysis…"))
        if self._engine.is_running:
            self._engine.stop()
        else:
            QtCore.QTimer.singleShot(0, self._start_engine_analysis)

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
        installed_families = set(QtGui.QFontDatabase.families())
        preferred_family = next(
            (family for family in ("Inter", "Noto Sans", "Segoe UI", "Helvetica Neue", "Arial") if family in installed_families),
            font.family(),
        )
        font.setFamily(preferred_family)
        font.setPointSize(size)
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.setFont(font)
        self.setFont(font)
        for widget in self.findChildren(QtWidgets.QWidget):
            widget.setFont(font)
        analysis_graph = getattr(self, "_analysis_graph", None)
        if analysis_graph is not None:
            analysis_graph.set_font_size(size)
        qml_workspace = getattr(self, "_qml_workspace", None)
        if qml_workspace is not None:
            qml_workspace.rootContext().setContextProperty("uiFontSize", size)
        game_tree = getattr(self, "_game_tree", None)
        if game_tree is not None:
            game_tree.set_font_size(size)

    def _apply_theme(self, theme: str) -> None:
        """Apply the shared NightyGo component theme."""
        self._ui_theme = theme
        apply_application_theme(theme, getattr(self, "_font_size", 14))
        if hasattr(self, "_board"):
            self._board.set_ui_theme(theme)
        if hasattr(self, "_game_tree"):
            self._game_tree.set_theme(theme)
        if hasattr(self, "_analysis_graph"):
            self._analysis_graph.set_theme(theme)
        if hasattr(self, "_qml_workspace"):
            self._qml_workspace.rootContext().setContextProperty("uiTheme", theme)

    def _refresh_navigation(self, *_args) -> None:
        self._next_button.setEnabled(self._controller.session.can_advance)

    def _populate_variations(self, selected_index: int = 0) -> None:
        children = self._controller.current_node.children
        self._variations.blockSignals(True)
        self._variations.clear()
        if not children:
            self._variations.addItem(self._t("Main line"))
        else:
            self._variations.addItem(self._t("Main line"))
            for number in range(2, len(children) + 1):
                self._variations.addItem(self._t("Variation {number}", number=number))
        self._variations.setCurrentIndex(min(max(0, selected_index), self._variations.count() - 1))
        self._variations.setEnabled(len(children) > 1)
        self._variations.blockSignals(False)

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

    def _current_analysis_position(self):
        return (self._controller.game, tuple(self._controller.root.values("KM")))

    def _refresh(self) -> None:
        self.game = self._controller.game
        self.setWindowTitle("NightyGo" + (" *" if self._controller.isDirty else ""))
        position_changed = self._analysis_position != self._current_analysis_position()
        if position_changed and self._analysis_requested and self._engine.status == GtpEngine.ANALYZING:
            self._analysis_restart_pending = True
            self._engine.stop_analysis()
        self._analysis_data.clear()
        self._last_root_metrics = None
        self._candidate_list.clear()
        self._analysis_summary.setText(self._t("Analysis not available for this move"))
        self._board.set_analysis_moves([], self.game.size)
        self._latest_ownership = ()
        self._board.set_ownership((), 0)
        self._board.set_markup(self._controller.current_node.properties)
        self._board.set_game(self.game)
        self._analysis_graph.set_current_move(max(0, len(self._controller.session.path) - 1))
        self._comment_editor.setPlainText(
            "\n".join(self._controller.current_node.values("C"))
        )
        self._refresh_tree()
        self._undo_button.setEnabled(self._controller.session.can_undo)
        self._redo_button.setEnabled(self._controller.session.can_advance)
        self._previous_button.setEnabled(self._controller.session.can_undo)
        self._populate_variations()
        self._next_button.setEnabled(self._controller.session.can_advance)
        if self.game.is_finished:
            self.statusBar().showMessage(self._t("Game ended after two passes"))
            self._toolbar_status.setText(self._t("Game ended after two passes"))
        else:
            color = self._t("Black" if self.game.to_play == BLACK else "White")
            self.statusBar().showMessage(self._t("{color} to play", color=color))
            self._toolbar_status.setText(self._t("{color} to play", color=color))
        self._capture_label.setText(
            self._t("Captured  Black: {black}   White: {white}", black=self.game.captures[BLACK], white=self.game.captures[WHITE])
        )
