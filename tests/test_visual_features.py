"""Regression coverage for visual materials and review graph interaction."""

import math
import os
import time
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtCore, QtGui, QtTest, QtWidgets

from nightygo.model import GoGame
from nightygo.ui.analysis_graph import AnalysisGraph
from nightygo.ui.board_widget import BoardWidget
from nightygo.ui.theme import _PALETTES


class VisualFeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_board_material_strength_clamps_and_fps_overlay_renders(self):
        board = BoardWidget()
        board.resize(500, 500)
        board.set_game(GoGame())
        board.set_board_material("Starfield")
        board.set_material_strength(140)
        board.set_performance_overlay(True)
        self.assertEqual(board._material_strength, 100)
        board.set_material_strength(0)
        self.assertEqual(board._material_strength, 0)
        image = QtGui.QImage(board.size(), QtGui.QImage.Format.Format_ARGB32)
        image.fill(QtCore.Qt.GlobalColor.transparent)
        board.render(image)
        self.assertFalse(image.isNull())
        self.assertGreater(board.render_fps, -1)

    def test_ambient_animation_phase_does_not_wrap_at_cycle_boundary(self):
        board = BoardWidget()
        board.set_motion_level("full")
        board._animation_started = time.monotonic() - (2 * math.pi / 1.65) - 0.02
        board._advance_theme_animation()
        before = board._animation_phase
        board._animation_started -= 20
        board._advance_theme_animation()
        self.assertGreater(before, 2 * math.pi)
        self.assertGreater(board._animation_phase, before + 30)

    def test_analysis_graph_click_selects_nearest_move_on_timeline(self):
        graph = AnalysisGraph()
        graph.resize(400, 160)
        graph.set_points([(0, 0.5), (30, 0.7), (60, 0.3)])
        selected = []
        graph.move_selected.connect(selected.append)
        QtTest.QTest.mouseClick(
            graph,
            QtCore.Qt.MouseButton.LeftButton,
            pos=QtCore.QPoint(200, 75),
        )
        self.assertEqual(len(selected), 1)
        self.assertGreaterEqual(selected[0], 0)
        self.assertLessEqual(selected[0], 60)

    def test_high_contrast_palette_has_bright_text_and_accent(self):
        palette = _PALETTES["High contrast"]
        self.assertEqual(palette["text"], "#ffffff")
        self.assertNotEqual(palette["accent"], palette["window"])


if __name__ == "__main__":
    unittest.main()
