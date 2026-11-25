# NightyGo

English | [繁體中文](README.zh-TW.md)

A PySide6 Go play, record-editing, and AI-review studio. It supports SGF
variations, board annotations, a local game library, KataGo live analysis and
full-game review. Choose a dark or warm-light theme, or preview the Qt Quick
board workspace.

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
- Edit game metadata, comments, main lines and variations, plus triangle, square, circle, cross, label, line and arrow markup.
- Search recent records by players, event, result and custom tags; unsaved games receive recovery snapshots.
- Configure a local KataGo executable for asynchronous candidate moves, win rate, score lead and ownership; review a full main line with a win-rate graph and jump links for major swings.
- Browse the live official KataGo model catalogue from **Settings → AI Model Center**. It recommends model tiers from currently available RAM and detectable NVIDIA VRAM, then downloads, cancels or selects a model for KataGo.
- Preview the Qt Quick board from **View → QML workspace preview**; choose a dark or warm-light theme, font size and animated sky preference in Settings.

Use **File → Open SGF** to load a record and **File → Save SGF** to save it.
AI analysis requires a KataGo executable; model files can be downloaded in the
AI Model Center and are stored under the application data directory's `models/`
folder. Choose **Download and use** to pass that model path to KataGo at launch.
Memory advice is an estimate based on currently available RAM/VRAM and model
architecture; actual needs also depend on the engine backend and search-cache
settings. Preferences also remember the placement sound, font size, theme,
animation and board/stone materials.
