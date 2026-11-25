"""Tests for SGF parsing, round trips, and game replay."""

import tempfile
import unittest
from pathlib import Path

from nightygo.model import BLACK, WHITE
from nightygo.sgf import (
    SgfCollection,
    SgfError,
    parse_sgf,
    read_sgf,
    serialize_sgf,
    write_sgf,
)
from nightygo.sgf_session import SgfGameSession


class SgfParserTest(unittest.TestCase):
    def test_round_trip_preserves_variations_and_unknown_properties(self) -> None:
        source = "(;GM[1]FF[4]SZ[9]XX[keep];B[aa](;W[bb]C[first])(;W[cc]C[second]))"
        collection = parse_sgf(source)
        self.assertEqual(parse_sgf(serialize_sgf(collection)), collection)

    def test_escapes_and_line_continuations(self) -> None:
        collection = parse_sgf(r"(;C[a\]b\\c\
continued])")
        self.assertEqual(collection.games[0].values("C"), ["a]b\\ccontinued"])

    def test_multiple_games_and_file_round_trip(self) -> None:
        collection = parse_sgf("(;SZ[9];B[aa])(;SZ[13];W[bb])")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "games.sgf"
            write_sgf(collection, path)
            self.assertEqual(read_sgf(path), collection)

    def test_rejects_malformed_collection(self) -> None:
        with self.assertRaises(SgfError):
            parse_sgf("(;B[aa]")


class SgfSessionTest(unittest.TestCase):
    def test_replays_setup_moves_and_passes(self) -> None:
        root = parse_sgf("(;SZ[9]AB[aa:ab]AW[cc]PL[W];W[dd];B[];W[])").games[0]
        session = SgfGameSession(root, start_at_end=True)
        self.assertEqual(session.game.board[0][0], BLACK)
        self.assertEqual(session.game.board[1][0], BLACK)
        self.assertEqual(session.game.board[2][2], WHITE)
        self.assertTrue(session.game.is_finished)
        self.assertEqual(len(session.game.moves), 3)

    def test_navigation_and_appending_retains_existing_variation(self) -> None:
        root = parse_sgf("(;SZ[9];B[aa](;W[bb])(;W[cc]))").games[0]
        session = SgfGameSession(root)
        session.next()
        self.assertEqual(session.game.board[0][0], BLACK)
        session.next(1)
        self.assertEqual(session.game.board[2][2], WHITE)
        session.previous()
        move = session.game.play(3, 3)
        session.append_move(move)
        self.assertEqual(len(root.children[0].children), 3)
        self.assertEqual(session.game.board[3][3], WHITE)

    def test_pass_is_exported_as_empty_move(self) -> None:
        session = SgfGameSession.new_game(9)
        move = session.game.pass_turn()
        session.append_move(move)
        self.assertIn(";B[]", serialize_sgf(SgfCollection([session.root])))

    def test_rejects_illegal_moves(self) -> None:
        root = parse_sgf("(;SZ[9];B[aa];W[aa])").games[0]
        with self.assertRaises(SgfError):
            SgfGameSession(root, start_at_end=True)


if __name__ == "__main__":
    unittest.main()
