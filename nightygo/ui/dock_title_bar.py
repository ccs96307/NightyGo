"""Large, accessible title-bar controls for dockable panels."""

from PySide6 import QtCore, QtWidgets
from nightygo.i18n import translate


class DockTitleBar(QtWidgets.QWidget):
    """Provide easy-to-hit expand/restore and close buttons."""

    def __init__(self, dock: QtWidgets.QDockWidget) -> None:
        super().__init__(dock)
        self._dock = dock
        self._language = "en"
        self.setFixedHeight(42)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 6, 2)
        layout.setSpacing(5)

        self._title = QtWidgets.QLabel(dock.windowTitle(), self)
        dock.windowTitleChanged.connect(self._title.setText)
        self._title.setStyleSheet("font-weight: 600;")
        layout.addWidget(self._title, 1)

        self._expand_button = QtWidgets.QToolButton(self)
        self._expand_button.setFixedSize(36, 36)
        self._expand_button.setIconSize(QtCore.QSize(20, 20))
        self._expand_button.clicked.connect(self._toggle_expanded)
        layout.addWidget(self._expand_button)

        self._close_button = QtWidgets.QToolButton(self)
        self._close_button.setFixedSize(36, 36)
        self._close_button.setIconSize(QtCore.QSize(20, 20))
        self._close_button.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton)
        )
        self._close_button.setToolTip(translate("Close panel", self._language))
        self._close_button.setAccessibleName(translate("Close panel", self._language))
        self._close_button.clicked.connect(dock.hide)
        layout.addWidget(self._close_button)

        dock.topLevelChanged.connect(self._update_expand_button)
        dock.visibilityChanged.connect(self._update_expand_button)
        self._update_expand_button()

    def _toggle_expanded(self) -> None:
        if self._dock.isFloating():
            if self._dock.isMaximized():
                self._dock.showNormal()
            else:
                self._dock.setFloating(False)
        else:
            self._dock.setFloating(True)
            self._dock.showMaximized()
        self._update_expand_button()

    def _update_expand_button(self, *_args) -> None:
        maximized = self._dock.isFloating() and self._dock.isMaximized()
        icon = (
            QtWidgets.QStyle.StandardPixmap.SP_TitleBarNormalButton
            if maximized
            else QtWidgets.QStyle.StandardPixmap.SP_TitleBarMaxButton
        )
        self._expand_button.setIcon(self.style().standardIcon(icon))
        label = translate("Restore panel" if maximized else "Expand panel", self._language)
        self._expand_button.setToolTip(label)
        self._expand_button.setAccessibleName(label)

    def set_language(self, language: str) -> None:
        self._language = language
        close_label = translate("Close panel", language)
        self._close_button.setToolTip(close_label)
        self._close_button.setAccessibleName(close_label)
        self._update_expand_button()
