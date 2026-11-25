"""Tests for the local SGF library index."""

import tempfile
import unittest
from pathlib import Path

from PySide6 import QtCore

from nightygo.library import GameLibrary


class GameLibraryTests(unittest.TestCase):
    def test_recent_search_and_tags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            game_path = base / "round-1.sgf"
            game_path.write_text("(;FF[4]SZ[9]PB[Alpha]PW[Beta]EV[Autumn Cup])", encoding="utf-8")
            settings = QtCore.QSettings(str(base / "settings.ini"), QtCore.QSettings.Format.IniFormat)
            library = GameLibrary(settings)
            library.touch(game_path)
            library.set_tags(game_path, ["tournament", "opening-study"])
            self.assertEqual(library.search("alpha"), [str(game_path.resolve())])
            self.assertEqual(library.search("opening-study"), [str(game_path.resolve())])
            self.assertEqual(library.tags(game_path), ["tournament", "opening-study"])


if __name__ == "__main__":
    unittest.main()
