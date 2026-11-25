# NightyGo web edition

A no-install browser prototype built with plain HTML, CSS, and JavaScript. There is no Node, Python, npm, or build dependency. It can be served as a static GitHub Pages site.

## Run locally

From the repository root:

```bash
python3 -m http.server 8000 --directory web
```

Open `http://localhost:8000`. WebGPU and offline caching require HTTPS or localhost; opening the page as a `file://` URL will disable those browser features.

## Implemented

- 9×9, 13×13, and 19×19 games with move preview, captures, suicide checks, simple ko, pass, and two-pass ending.
- Undo, redo, previous/next navigation, and a clickable SGF variation tree that keeps continuations on a line and forks at variations.
- SGF FF[4] import and export with variation/property retention. SGF collections currently open their first game only.
- Game metadata and current-node comments.
- Browser-local game library, search, automatic recovery, and offline asset caching.
- Light/dark theme, five placement sounds, four capture sound bands, font size, board/stone materials, and motion preferences.
- Language selector for Traditional and Simplified Chinese, English, Japanese, and Korean. A few secondary status messages may still fall back to English.
- WebGPU capability detection and a browser memory hint where available.

## Not implemented yet

WebGPU detection does not execute an AI model. The browser edition does not yet bundle or connect KataGo WebGPU/WASM, download models, show candidate moves/win-rate/ownership, or review a full game. Shape and label annotations can be edited; line/arrow creation, multi-game SGF selection, library tags, and the full desktop AI/model center are not ported. Game library data lives in this browser's local storage; export SGF backups before clearing site data.

Placement and capture sound files are shared with the desktop app; their attribution and licensing notes are in [`assets/sounds/SOURCES.md`](assets/sounds/SOURCES.md).
