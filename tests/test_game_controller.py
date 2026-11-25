"""Tests for the presentation-independent game controller."""

import tempfile
import unittest
from pathlib import Path

from nightygo.game_controller import GameController
from nightygo.sgf import parse_sgf, serialize_sgf
from nightygo.sgf_session import SgfGameSession


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
        self.assertFalse(controller.isDirty)
        controller.play_at(3, 3)
        self.assertTrue(controller.isDirty)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "game.sgf"
            self.assertTrue(controller.save_sgf(path))
            self.assertFalse(controller.isDirty)
            reopened = GameController()
            self.assertTrue(reopened.load_sgf(path))

        self.assertEqual(reopened.moveCount, 1)
        self.assertEqual(reopened.game.board[3][3], 1)

    def test_edits_game_info_markup_and_variations(self) -> None:
        controller = GameController()
        collection = parse_sgf("(;SZ[9];B[dd](;W[cc])(;W[ee]))")
        controller.collection = collection
        controller.session = SgfGameSession(collection.games[0])
        branch_parent = collection.games[0].children[0]
        controller.navigate_to(branch_parent.children[1])
        controller.make_current_variation_mainline()
        self.assertEqual(branch_parent.children[0].values("W"), ["ee"])
        controller.delete_current_variation()
        self.assertIs(controller.current_node, branch_parent)

        controller.set_game_info({"PB": "Alpha", "KM": "7.5"})
        controller.add_markup("triangle", 4, 4)
        controller.add_markup("label", 3, 3, "A")
        serialized = serialize_sgf(controller.collection)
        self.assertIn("PB[Alpha]", serialized)
        self.assertIn("KM[7.5]", serialized)
        self.assertIn("TR[ee]", serialized)
        self.assertIn("LB[dd:A]", serialized)

    def test_recovery_round_trip_remains_unsaved(self) -> None:
        controller = GameController()
        controller.play_at(3, 3)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recovery.sgf"
            controller.save_recovery(path)
            restored = GameController()
            self.assertTrue(restored.load_recovery(path))
        self.assertEqual(restored.moveCount, 1)
        self.assertTrue(restored.isDirty)


if __name__ == "__main__":
    unittest.main()
