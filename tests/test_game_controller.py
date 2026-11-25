"""Tests for the presentation-independent game controller."""

import tempfile
import unittest
from pathlib import Path

from nightygo.game_controller import GameController


class GameControllerTests(unittest.TestCase):
    def test_play_undo_redo_and_comment_edit(self) -> None:
        controller = GameController()
        self.assertTrue(controller.play_at(3, 3))
        self.assertEqual(controller.moveCount, 1)
        self.assertTrue(controller.undo())
        self.assertTrue(controller.redo())
        controller.set_current_comment("Good opening")
        self.assertEqual(controller.current_node.values("C"), ["Good opening"])

    def test_save_and_reopen_preserves_game_tree(self) -> None:
        controller = GameController()
        controller.play_at(3, 3)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "game.sgf"
            self.assertTrue(controller.save_sgf(path))
            reopened = GameController()
            self.assertTrue(reopened.load_sgf(path))

        self.assertEqual(reopened.moveCount, 1)
        self.assertEqual(reopened.game.board[3][3], 1)


if __name__ == "__main__":
    unittest.main()
