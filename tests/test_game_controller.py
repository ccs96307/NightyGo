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

    def test_saving_twice_persists_the_second_edit(self) -> None:
        controller = GameController()
        self.assertTrue(controller.play_at(3, 3))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "game.sgf"
            self.assertTrue(controller.save_sgf(path))
            controller.set_current_comment("saved on the second write")
            self.assertTrue(controller.save_sgf())
            saved = parse_sgf(path.read_text(encoding="utf-8"))
        self.assertEqual(saved.games[0].children[0].values("C"), ["saved on the second write"])
        self.assertFalse(controller.isDirty)

    def test_invalid_game_info_does_not_partially_mutate_root(self) -> None:
        controller = GameController()
        controller.set_game_info({"PB": "Alpha", "INVALID": "value"})
        self.assertEqual(controller.root.values("PB"), [])
        self.assertIn("Unsupported game-info property", controller.last_error)

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

    def test_move_count_counts_root_move_and_skips_annotations(self) -> None:
        controller = GameController()
        root = parse_sgf("(;SZ[9]B[aa];C[position];C[end])").games[0]
        controller.session = SgfGameSession(root, start_at_end=True)
        self.assertEqual(controller.moveCount, 1)

    def test_selecting_an_invalid_branch_leaves_previous_position_usable(self) -> None:
        controller = GameController()
        root = parse_sgf("(;SZ[9];B[cc](;W[dd])(;W[cc]))").games[0]
        controller.session = SgfGameSession(root)
        self.assertTrue(controller.next())
        previous_game = controller.game
        for navigate in (lambda: controller.next(1), lambda: controller.navigate_to(root.children[0].children[1])):
            self.assertFalse(navigate())
            self.assertIs(controller.current_node, root.children[0])
            self.assertIs(controller.game, previous_game)
        self.assertTrue(controller.next(0))

    def test_editing_duplicate_variations_targets_selected_node(self) -> None:
        controller = GameController()
        root = parse_sgf("(;SZ[9](;B[cc])(;B[cc]))").games[0]
        first, second = root.children
        controller.session = SgfGameSession(root)
        controller.navigate_to(second)
        self.assertTrue(controller.make_current_variation_mainline())
        self.assertIs(root.children[0], second)
        controller.navigate_to(first)
        self.assertTrue(controller.delete_current_variation())
        self.assertEqual(len(root.children), 1)
        self.assertIs(root.children[0], second)

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
