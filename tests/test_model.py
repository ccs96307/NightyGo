"""Unit tests for the interface-independent Go rules model."""

import unittest

from nightygo.model import BLACK, EMPTY, WHITE, GoGame, IllegalMove


class GoGameTests(unittest.TestCase):
    def test_turns_alternate_and_board_is_immutable_snapshot(self) -> None:
        game = GoGame(size=9)
        initial_board = game.board

        move = game.play(4, 4)

        self.assertEqual(move.color, BLACK)
        self.assertEqual(game.board[4][4], BLACK)
        self.assertEqual(game.to_play, WHITE)
        self.assertEqual(initial_board[4][4], EMPTY)

    def test_rejects_occupied_and_out_of_bounds_points(self) -> None:
        game = GoGame(size=9)
        game.play(0, 0)

        with self.assertRaises(IllegalMove):
            game.play(0, 0)
        with self.assertRaises(IllegalMove):
            game.play(-1, 0)
        with self.assertRaises(IllegalMove):
            game.play(9, 0)

    def test_captures_a_group_without_liberties(self) -> None:
        game = GoGame(size=9)
        game.play(0, 1)  # B
        game.play(1, 1)  # W
        game.play(1, 0)  # B
        game.play(8, 8)  # W
        game.play(2, 1)  # B
        game.play(7, 8)  # W

        move = game.play(1, 2)  # B

        self.assertEqual(move.captured, ((1, 1),))
        self.assertEqual(game.board[1][1], EMPTY)
        self.assertEqual(game.captures[BLACK], 1)

    def test_rejects_suicide(self) -> None:
        game = GoGame(size=9)
        game.play(8, 8)  # B
        game.play(0, 1)  # W
        game.play(8, 7)  # B
        game.play(2, 1)  # W
        game.play(7, 8)  # B
        game.play(1, 0)  # W
        game.play(7, 7)  # B
        game.play(1, 2)  # W

        board_before = game.board
        with self.assertRaisesRegex(IllegalMove, "Suicide"):
            game.play(1, 1)
        self.assertEqual(game.board, board_before)
        self.assertEqual(game.to_play, BLACK)

    def test_rejects_immediate_ko_recapture(self) -> None:
        game = GoGame(size=9)
        game.play(0, 1)  # B
        game.play(1, 1)  # W, the ko stone
        game.play(2, 1)  # B
        game.play(0, 2)  # W
        game.play(1, 0)  # B
        game.play(2, 2)  # W
        game.play(8, 8)  # B
        game.play(1, 3)  # W
        capture = game.play(1, 2)  # B captures at (1, 1)

        self.assertIn((1, 1), capture.captured)
        board_after_capture = game.board
        with self.assertRaisesRegex(IllegalMove, "ko"):
            game.play(1, 1)
        self.assertEqual(game.board, board_after_capture)
        self.assertEqual(game.to_play, WHITE)

    def test_two_consecutive_passes_end_the_game(self) -> None:
        game = GoGame(size=9)
        first_pass = game.pass_turn()
        self.assertIsNone(first_pass.point)
        self.assertEqual(game.to_play, WHITE)
        self.assertFalse(game.is_finished)

        game.pass_turn()

        self.assertTrue(game.is_finished)
        with self.assertRaises(IllegalMove):
            game.play(4, 4)


    def test_undo_restores_move_turn_and_last_move(self) -> None:
        game = GoGame(size=9)
        game.play(4, 4)

        undone = game.undo()

        self.assertEqual(undone.point, (4, 4))
        self.assertEqual(game.board[4][4], EMPTY)
        self.assertEqual(game.to_play, BLACK)
        self.assertIsNone(game.last_move)
        self.assertFalse(game.can_undo)

    def test_undo_restores_captured_stones_and_capture_count(self) -> None:
        game = GoGame(size=9)
        game.play(0, 1)  # B
        game.play(1, 1)  # W
        game.play(1, 0)  # B
        game.play(8, 8)  # W
        game.play(2, 1)  # B
        game.play(7, 8)  # W
        game.play(1, 2)  # B captures

        game.undo()

        self.assertEqual(game.board[1][1], WHITE)
        self.assertEqual(game.captures[BLACK], 0)
        self.assertEqual(game.to_play, BLACK)

    def test_undo_restores_pass_and_finished_state(self) -> None:
        game = GoGame(size=9)
        game.pass_turn()
        game.pass_turn()
        self.assertTrue(game.is_finished)

        game.undo()

        self.assertFalse(game.is_finished)
        self.assertEqual(game.to_play, WHITE)
        self.assertEqual(len(game.moves), 1)

    def test_undo_without_moves_is_rejected(self) -> None:
        game = GoGame(size=9)
        with self.assertRaisesRegex(IllegalMove, "no moves"):
            game.undo()


if __name__ == "__main__":
    unittest.main()
