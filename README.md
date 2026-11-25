# NightyGo

English | [繁體中文](README.zh-TW.md)

A Go game record editor built with PySide6. It supports move previews, placement
sound, undo, and SGF import/export with variation navigation.

## Development setup

This project uses uv and PySide6. From the repository root, run:

```bash
uv sync --locked
uv run python -m nightygo
```

## Features

- Play and pass on a 19×19 board, with captures, suicide prevention, and simple ko.
- Preview a translucent stone before placing it and hear a placement sound.
- Undo moves and browse SGF game variations.
- Import and export SGF collections while preserving annotations and alternate lines.

Use **File → Open SGF** to load a record and **File → Save SGF** to save it.
