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
- Configure the KataGo engine and model together in **Settings → AI Model Center**. It recommends model tiers from available RAM / NVIDIA VRAM, installs a compatible official OpenCL engine on 64-bit Linux and Windows, and downloads/selects network models.
- Use KataGo for asynchronous candidate moves, win rate, score lead and ownership; review a full main line with a win-rate graph and jump links for major swings.
- Preview the Qt Quick board from **View → QML workspace preview**; choose a dark or warm-light theme, font size and motion level (off / subtle / full) in Settings. Move placement, capture, preview and tree navigation use short, low-distraction transitions.

Use **File → Open SGF** to load a record and **File → Save SGF** to save it.
AI setup is managed in AI Model Center. Select a network and choose **Download
engine and configure selected AI** to install the official engine and fetch/select
the network in one workflow. Existing engine binaries and advanced launch
arguments are also managed there. Models and managed engines are stored under
the application data directory. Automatic engine installation currently targets
64-bit Linux and Windows using official OpenCL packages; other systems can select
an existing KataGo binary. Memory advice uses available RAM/VRAM and model
architecture; actual needs also depend on backend and search-cache settings.
Preferences preview sound, font size, theme, motion and board/stone materials
as you change them. Choose **OK** to save, or **Cancel** to restore the previous
settings.
Use the language selector in the top toolbar to switch the interface among
English, Traditional Chinese, Simplified Chinese, Japanese and Korean; the
selection is remembered.
