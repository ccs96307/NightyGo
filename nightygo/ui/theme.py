"""NightyGo's compact visual system for the native Qt interface."""

from __future__ import annotations

from PySide6 import QtGui, QtWidgets


_PALETTES = {
    "Dark": {
        "window": "#0b1018",
        "surface": "#111a26",
        "raised": "#172333",
        "input": "#0d1520",
        "text": "#edf3fb",
        "muted": "#9aa9bd",
        "border": "#26364a",
        "accent": "#69e2cf",
        "accent_text": "#071a1a",
        "hover": "#1d2b3c",
        "selected": "#234b50",
        "danger": "#ff8e83",
    },
    "Warm light": {
        "window": "#eceff3",
        "surface": "#f8fafc",
        "raised": "#ffffff",
        "input": "#f3f6f9",
        "text": "#1d2937",
        "muted": "#68788b",
        "border": "#d7e0e9",
        "accent": "#087e76",
        "accent_text": "#f6fffd",
        "hover": "#e6f1f0",
        "selected": "#d1e9e6",
        "danger": "#b34f45",
    },
}


def apply_application_theme(theme: str, font_size: int = 14) -> None:
    """Apply NightyGo's palette and component styling to the active app."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        return
    colors = _PALETTES.get(theme, _PALETTES["Dark"])
    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(colors["window"]))
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(colors["text"]))
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(colors["input"]))
    palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(colors["surface"]))
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(colors["text"]))
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(colors["raised"]))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(colors["text"]))
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(colors["accent"]))
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(colors["accent_text"]))
    palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(colors["accent"]))
    palette.setColor(QtGui.QPalette.ColorRole.LinkVisited, QtGui.QColor(colors["accent"]))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(colors["raised"]))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(colors["text"]))
    app.setPalette(palette)

    c = colors
    brand_size = max(10.0, font_size * 1.0)
    caption_size = max(8.0, font_size * 0.64)
    status_size = max(8.0, font_size * 0.86)
    panel_title_size = max(9.0, font_size * 0.82)
    hero_size = max(14.0, font_size * 1.25)
    card_size = max(9.0, font_size * 0.72)
    footnote_size = max(8.0, font_size * 0.68)
    app.setStyleSheet(f"""
        QWidget {{ color: {c['text']}; }}
        QMainWindow, QDialog {{ background: {c['window']}; }}
        QMenuBar {{ background: {c['window']}; border: none; border-bottom: 1px solid {c['border']}; padding: 4px 8px; }}
        QMenuBar::item {{ background: transparent; border-radius: 6px; padding: 7px 10px; }}
        QMenuBar::item:selected, QMenu::item:selected {{ background: {c['hover']}; }}
        QMenu {{ background: {c['raised']}; border: 1px solid {c['border']}; border-radius: 9px; padding: 6px; }}
        QMenu::item {{ border-radius: 5px; padding: 7px 30px 7px 12px; }}
        QMenu::separator {{ height: 1px; background: {c['border']}; margin: 5px 8px; }}
        QToolBar {{ background: {c['surface']}; border: none; border-bottom: 1px solid {c['border']}; spacing: 8px; padding: 7px 12px; }}
        QToolBar::separator {{ width: 1px; background: {c['border']}; margin: 5px 8px; }}
        QLabel#brandMark {{ color: {c['accent']}; font-size: {brand_size:.1f}pt; font-weight: 800; letter-spacing: 2px; }}
        QLabel#brandCaption {{ color: {c['muted']}; font-size: {caption_size:.1f}pt; font-weight: 600; letter-spacing: 1px; }}
        QLabel#toolbarStatus {{ background: {c['raised']}; border: 1px solid {c['border']}; border-radius: 13px; padding: 5px 11px; color: {c['accent']}; font-size: {status_size:.1f}pt; font-weight: 700; }}
        QLabel#dialogHero {{ color: {c['text']}; font-size: {hero_size:.1f}pt; font-weight: 750; padding: 5px 2px 9px; }}
        QLabel#hardwareSummary, QLabel#modelDetails {{ background: {c['surface']}; border: 1px solid {c['border']}; border-radius: 12px; padding: 12px 14px; }}
        QLabel#hardwareSummary {{ font-size: {card_size:.1f}pt; }}
        QLabel#modelStatus {{ background: {c['raised']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 8px 10px; color: {c['muted']}; }}
        QLabel#emptyState {{ background: {c['surface']}; color: {c['muted']}; border: 1px dashed {c['border']}; border-radius: 10px; padding: 24px; }}
        QLabel#modelFootnote {{ color: {c['muted']}; font-size: {footnote_size:.1f}pt; }}
        QWidget#controlsSurface {{ background: {c['surface']}; }}
        QDockWidget {{ background: {c['surface']}; border: 1px solid {c['border']}; }}
        QDockWidget::title {{ padding: 0; height: 0; }}
        QWidget#dockTitleBar {{ background: {c['surface']}; border-bottom: 1px solid {c['border']}; }}
        QLabel#dockTitle {{ font-size: {panel_title_size:.1f}pt; font-weight: 700; }}
        QDockWidget::pane {{ border: 1px solid {c['border']}; }}
        QTabBar::tab {{ background: {c['surface']}; color: {c['muted']}; border: 1px solid {c['border']}; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; padding: 8px 14px; margin-right: 3px; }}
        QTabBar::tab:selected {{ background: {c['raised']}; color: {c['text']}; border-color: {c['accent']}; }}
        QPushButton, QToolButton {{ background: {c['raised']}; color: {c['text']}; border: 1px solid {c['border']}; border-radius: 8px; min-height: 34px; padding: 3px 13px; font-weight: 600; }}
        QPushButton:hover, QToolButton:hover {{ background: {c['hover']}; border-color: {c['accent']}; }}
        QPushButton:pressed, QToolButton:pressed {{ background: {c['selected']}; }}
        QPushButton:disabled, QToolButton:disabled {{ color: {c['muted']}; background: {c['surface']}; border-color: {c['border']}; }}
        QPushButton[variant="primary"] {{ background: {c['accent']}; color: {c['accent_text']}; border-color: {c['accent']}; }}
        QPushButton[variant="primary"]:hover {{ background: {c['accent']}; border-color: {c['accent']}; }}
        QPushButton[variant="secondary"] {{ background: transparent; color: {c['accent']}; border-color: {c['accent']}; }}
        QToolButton[variant="quiet"] {{ background: transparent; border-color: transparent; }}
        QLineEdit, QPlainTextEdit, QTextEdit, QListWidget, QTreeWidget, QTreeView, QComboBox, QSpinBox, QDoubleSpinBox {{ background: {c['input']}; color: {c['text']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 7px 9px; selection-background-color: {c['accent']}; selection-color: {c['accent_text']}; }}
        QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QListWidget:focus, QTreeWidget:focus, QComboBox:focus, QSpinBox:focus {{ border-color: {c['accent']}; }}
        QComboBox::drop-down {{ border: none; width: 28px; }}
        QComboBox QAbstractItemView {{ background: {c['raised']}; border: 1px solid {c['border']}; selection-background-color: {c['selected']}; padding: 4px; }}
        QCheckBox, QRadioButton {{ spacing: 9px; }}
        QCheckBox::indicator, QRadioButton::indicator {{ width: 18px; height: 18px; }}
        QCheckBox::indicator {{ border: 1px solid {c['border']}; border-radius: 5px; background: {c['input']}; }}
        QCheckBox::indicator:checked {{ background: {c['accent']}; border-color: {c['accent']}; }}
        QHeaderView::section {{ background: {c['surface']}; color: {c['muted']}; border: none; border-bottom: 1px solid {c['border']}; padding: 9px 10px; font-weight: 700; }}
        QTreeWidget::item, QListWidget::item {{ min-height: 30px; padding: 4px 6px; border-radius: 5px; }}
        QTreeWidget::item:selected, QListWidget::item:selected {{ background: {c['selected']}; color: {c['text']}; }}
        QTreeWidget::item:hover, QListWidget::item:hover {{ background: {c['hover']}; }}
        QGroupBox {{ border: 1px solid {c['border']}; border-radius: 10px; margin-top: 12px; padding: 12px 10px 8px; font-weight: 700; }}
        QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 5px; color: {c['muted']}; }}
        QProgressBar {{ background: {c['input']}; border: 1px solid {c['border']}; border-radius: 6px; min-height: 12px; text-align: center; color: {c['text']}; }}
        QProgressBar::chunk {{ background: {c['accent']}; border-radius: 5px; }}
        QStatusBar {{ background: {c['surface']}; color: {c['muted']}; border-top: 1px solid {c['border']}; }}
        QStatusBar::item {{ border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 12px; margin: 3px; }}
        QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 3px; }}
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{ background: {c['border']}; border-radius: 5px; min-width: 28px; min-height: 28px; }}
        QScrollBar::handle:hover {{ background: {c['muted']}; }}
        QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
        QToolTip {{ color: {c['text']}; background: {c['raised']}; border: 1px solid {c['border']}; padding: 5px 8px; }}
        QSplitter::handle {{ background: {c['border']}; }}
    """)
