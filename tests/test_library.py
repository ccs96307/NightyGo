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

    def test_ignores_malformed_saved_tags_and_recent_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            settings = QtCore.QSettings(str(Path(directory) / "settings.ini"), QtCore.QSettings.Format.IniFormat)
            settings.setValue("library/tags", '{"/tmp/game.sgf": 42, "/tmp/other.sgf": ["ok", 3]}')
            settings.setValue("library/recent", 42)
            library = GameLibrary(settings)
            self.assertEqual(library.tags("/tmp/game.sgf"), [])
            self.assertEqual(library.tags("/tmp/other.sgf"), ["ok"])
            self.assertEqual(library.recent_paths, [])


if __name__ == "__main__":
    unittest.main()
