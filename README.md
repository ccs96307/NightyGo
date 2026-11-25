# NightyGo

English | [繁體中文](README.zh-TW.md)

A Go game record editor built with PySide6. It supports move previews, placement
sound, undo, SGF import/export, and a clickable game tree for browsing variations.

## Development setup

This project uses uv and PySide6. From the repository root, run:

```bash
uv sync --locked
uv run --locked python -m nightygo
```

Application logs include timestamps, severity levels, and module names. Set
`NIGHTYGO_LOG_LEVEL=DEBUG` before launch to enable diagnostic details.

## Features

- Play and pass on a 19×19 board, with captures, suicide prevention, and simple ko.
- Preview a translucent stone before placing it and choose among five real Go-stone recordings.
- Choose wood, starfield, or night-sky board surfaces and traditional, starfield, or moonstone stones.
- Undo moves and click any node in the game tree to jump to that position or browse variations.
- Import and export SGF collections while preserving annotations and alternate lines.

Use **File → Open SGF** to load a record and **File → Save SGF** to save it.
Use **Settings → Preferences** to preview a Go-stone sound, adjust the font size,
or choose the board and stone materials. Preferences are remembered. Both side
panels have larger expand/restore and close controls in their title bars.
