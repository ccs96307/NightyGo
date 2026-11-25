# NightyGo

English | [繁體中文](README.zh-TW.md)

A Go game record editor built with PySide6. It supports move previews, placement
sound, undo, SGF import/export, and a clickable game tree for browsing variations.

## Development setup

This project uses uv and PySide6. From the repository root, run:

```bash
uv sync --locked
uv run python -m nightygo
```

## Features

- Play and pass on a 19×19 board, with captures, suicide prevention, and simple ko.
- Preview a translucent stone before placing it and choose among five real Go-stone recordings.
- Undo moves and click any node in the game tree to jump to that position or browse variations.
- Import and export SGF collections while preserving annotations and alternate lines.

Use **File → Open SGF** to load a record and **File → Save SGF** to save it.
Use **Settings → Preferences** to select and preview a Go-stone placement sound
or change the application font size. The default size is 14 pt, and preferences
are remembered.
