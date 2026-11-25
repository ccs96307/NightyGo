"""Small local SGF library backed by the user's application settings."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6 import QtCore

from nightygo.sgf import read_sgf


class GameLibrary:
    """Track recent SGF files and user labels without copying game files."""

    def __init__(self, settings: QtCore.QSettings) -> None:
        self._settings = settings

    @property
    def recent_paths(self) -> list[str]:
        values = self._settings.value("library/recent", [])
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list):
            return []
        return [path for path in values if isinstance(path, str) and Path(path).is_file()]

    def touch(self, path: str | Path) -> None:
        normalized = str(Path(path).expanduser().resolve())
        paths = [normalized, *(item for item in self.recent_paths if item != normalized)]
        self._settings.setValue("library/recent", paths[:100])

    def tags(self, path: str | Path) -> list[str]:
        mapping = self._read_tags()
        return mapping.get(str(Path(path).expanduser().resolve()), [])

    def set_tags(self, path: str | Path, tags: list[str]) -> None:
        mapping = self._read_tags()
        key = str(Path(path).expanduser().resolve())
        clean = list(dict.fromkeys(tag.strip() for tag in tags if tag.strip()))
        if clean:
            mapping[key] = clean
        else:
            mapping.pop(key, None)
        self._settings.setValue("library/tags", json.dumps(mapping, ensure_ascii=False))

    def search(self, query: str = "") -> list[str]:
        query = query.casefold().strip()
        found = []
        mapping = self._read_tags()
        for path in self.recent_paths:
            haystack = Path(path).name.casefold() + " " + " ".join(mapping.get(path, [])).casefold()
            try:
                game = read_sgf(path).games[0]
                haystack += " " + " ".join(value for key in ("PB", "PW", "EV", "DT", "RE") for value in game.values(key)).casefold()
            except (OSError, ValueError):
                pass
            if not query or query in haystack:
                found.append(path)
        return found

    def _read_tags(self) -> dict[str, list[str]]:
        try:
            value = json.loads(str(self._settings.value("library/tags", "{}")))
        except (TypeError, json.JSONDecodeError):
            return {}
        if not isinstance(value, dict):
            return {}
        return {
            str(path): [tag for tag in tags if isinstance(tag, str)]
            for path, tags in value.items()
            if isinstance(tags, list)
        }
