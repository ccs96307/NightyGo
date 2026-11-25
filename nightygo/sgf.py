"""SGF FF[4] collection parser and serializer.

The parser retains unknown properties and ordered variation trees so files can
round-trip without discarding comments, annotations, or alternate lines.
"""

from __future__ import annotations

import codecs
import re
from dataclasses import dataclass, field
from itertools import pairwise
from pathlib import Path

from PySide6 import QtCore


class SgfError(ValueError):
    """Raised when an SGF collection is malformed or unsupported."""


@dataclass
class SgfNode:
    """Properties and child variations for one SGF node."""

    properties: dict[str, list[str]] = field(default_factory=dict)
    children: list[SgfNode] = field(default_factory=list)

    def values(self, identifier: str) -> list[str]:
        """Return all values for a property identifier."""
        return self.properties.get(identifier, [])


@dataclass
class SgfCollection:
    """One or more ordered SGF game trees."""

    games: list[SgfNode] = field(default_factory=list)


class _Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.index = 0

    def parse_collection(self) -> SgfCollection:
        collection = SgfCollection()
        self._skip_whitespace()
        while self.index < len(self.text):
            if self._peek() != "(":
                self._error("Expected a game tree")
            collection.games.append(self._parse_tree())
            self._skip_whitespace()
        if not collection.games:
            self._error("The SGF collection is empty")
        return collection

    def _parse_tree(self) -> SgfNode:
        self._expect("(")
        self._skip_whitespace()
        sequence: list[SgfNode] = []
        while self._peek() == ";":
            sequence.append(self._parse_node())
            self._skip_whitespace()
        if not sequence:
            self._error("A game tree must contain a node")
        for current, following in pairwise(sequence):
            current.children.append(following)
        last = sequence[-1]
        while self._peek() == "(":
            last.children.append(self._parse_tree())
            self._skip_whitespace()
        self._expect(")")
        return sequence[0]

    def _parse_node(self) -> SgfNode:
        self._expect(";")
        node = SgfNode()
        self._skip_whitespace()
        while self._is_upper(self._peek()):
            start = self.index
            while self._is_upper(self._peek()):
                self.index += 1
            identifier = self.text[start:self.index]
            values: list[str] = []
            self._skip_whitespace()
            while self._peek() == "[":
                values.append(self._parse_value())
                self._skip_whitespace()
            if not values:
                self._error(f"Property {identifier} has no value")
            if identifier in node.properties:
                node.properties[identifier].extend(values)
            else:
                node.properties[identifier] = values
        return node

    def _parse_value(self) -> str:
        self._expect("[")
        value: list[str] = []
        while self.index < len(self.text):
            character = self.text[self.index]
            self.index += 1
            if character == "]":
                return "".join(value)
            if character == "\\":
                if self.index >= len(self.text):
                    self._error("Unterminated escape sequence")
                escaped = self.text[self.index]
                self.index += 1
                if escaped == "\r":
                    if self._peek() == "\n":
                        self.index += 1
                    continue
                if escaped == "\n":
                    continue
                value.append(escaped)
            else:
                value.append(character)
        self._error("Unterminated property value")

    def _skip_whitespace(self) -> None:
        while self.index < len(self.text) and self.text[self.index].isspace():
            self.index += 1

    def _peek(self) -> str:
        return self.text[self.index] if self.index < len(self.text) else ""

    def _expect(self, character: str) -> None:
        if self._peek() != character:
            self._error(f"Expected {character!r}")
        self.index += 1

    def _error(self, message: str):
        raise SgfError(f"{message} at character {self.index}")

    @staticmethod
    def _is_upper(character: str) -> bool:
        return "A" <= character <= "Z"


def parse_sgf(text: str) -> SgfCollection:
    """Parse an SGF collection while preserving variations and properties."""
    return _Parser(text).parse_collection()


def serialize_sgf(collection: SgfCollection) -> str:
    """Serialize an SGF collection as FF[4]-style text."""
    return "".join(_serialize_tree(game) for game in collection.games)


def read_sgf(path: str | Path) -> SgfCollection:
    """Read an SGF file using its declared FF[4] character encoding."""
    data = Path(path).read_bytes()
    if data.startswith(codecs.BOM_UTF8):
        text = data.decode("utf-8-sig")
    else:
        header = data[:8192].decode("ascii", errors="ignore")
        encoding_match = re.search(r"\bCA\[([^\]]+)\]", header)
        encoding = encoding_match.group(1) if encoding_match else "ISO-8859-1"
        try:
            text = data.decode(encoding)
        except (LookupError, UnicodeDecodeError) as error:
            raise SgfError(f"Could not decode SGF with charset {encoding!r}") from error
    return parse_sgf(text)


def write_sgf(collection: SgfCollection, path: str | Path) -> None:
    """Atomically save an SGF collection as UTF-8."""
    save_file = QtCore.QSaveFile(str(Path(path)))
    if not save_file.open(QtCore.QIODevice.OpenModeFlag.WriteOnly):
        raise OSError(save_file.errorString())
    normalized_games = []
    for game in collection.games:
        properties = dict(game.properties)
        properties["CA"] = ["UTF-8"]
        normalized_games.append(SgfNode(properties, game.children))
    payload = serialize_sgf(SgfCollection(normalized_games)).encode("utf-8")
    written = save_file.write(payload)
    if written != len(payload):
        save_file.cancelWriting()
        raise OSError(save_file.errorString() or "Could not write the complete SGF file")
    if not save_file.commit():
        raise OSError(save_file.errorString())


def _serialize_tree(root: SgfNode) -> str:
    parts = ["("]
    node = root
    while True:
        parts.append(_serialize_node(node))
        if not node.children:
            break
        if len(node.children) == 1:
            node = node.children[0]
            continue
        parts.extend(_serialize_tree(child) for child in node.children)
        break
    parts.append(")")
    return "".join(parts)


def _serialize_node(node: SgfNode) -> str:
    parts = [";"]
    for identifier, values in node.properties.items():
        if not identifier or not all("A" <= char <= "Z" for char in identifier):
            raise SgfError(f"Invalid property identifier: {identifier!r}")
        if not values:
            raise SgfError(f"Property {identifier} has no values")
        parts.append(identifier)
        for value in values:
            escaped = value.replace("\\", "\\\\").replace("]", "\\]")
            parts.extend(("[", escaped, "]"))
    return "".join(parts)
