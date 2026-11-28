# NightyGo web edition

NightyGo Web is an install-free Go study studio built with HTML, CSS, JavaScript, and a KataGo WebAssembly engine. AI models are downloaded by the user and stored in browser IndexedDB; inference runs locally in the browser.

## Run locally

From the repository root:

```bash
python3 -m http.server 8000 --directory web
```

Open `http://localhost:8000`. WebGPU and offline caching require HTTPS or localhost; opening the page as a `file://` URL will disable those browser features.

## Implemented

- 9×9, 13×13, and 19×19 games with move preview, captures, suicide checks, simple ko, pass, and two-pass ending.
- Undo, redo, navigation, and a clickable SGF variation tree that forks at variations.
- FF[4] SGF collection import/export, game selection, variation trees, and node properties.
- Game metadata and current-node comments.
- Browser-local game library, search, automatic recovery, and offline asset caching.
- Light/dark theme, placement and capture sounds, font size, board/stone materials, and motion preferences.
- Traditional and Simplified Chinese, English, Japanese, and Korean.
- KataGo WASM model loading, WebGPU/CPU inference, candidate moves, win rate/score lead, ownership overlay, MCTS moves, and main-line review.
- AI Model Config with official light, balanced, and latest model download links plus an approximate memory recommendation. On GitHub Pages, select a model to download, install and load it directly. Local development checkouts can import a .bin.gz file.
- WebGPU/device detection, PWA offline cache, and SGF parser unit tests.

## Limits

The browser engine uses single-threaded MCTS, so it is slower than desktop KataGo's multithreaded search. WebGPU depends on the browser, GPU driver, and secure context (HTTPS/localhost); otherwise CPU inference may be slow. The Pages build bundles three pinned networks with the site. A local checkout includes the engine and can load a network through the file picker. Memory recommendations are approximate. AI search supports standard handicap positions with two or more initial black stones; it does not support AW/AE setup positions or later edited boards. Full-game review analyzes the main line and is capped at 250 moves. Browser data is local; export SGF backups before clearing site data.

Run tests with `node --test web/tests/*.test.js`. Rebuild the browser engine with `EMSDK_DIR=/path/to/emsdk bash scripts/build-web-engine.sh`; this requires Emscripten 7.0.1, Eigen 3, and network access for the WebGPU build port. The GitHub Pages workflow builds and deploys the static app.

The engine code is MIT licensed; see [`assets/engine/UPSTREAM-LICENSE`](assets/engine/UPSTREAM-LICENSE). KataGo network files have their own model licenses; review the official model page before use.

Placement and capture sound files are shared with the desktop app; their attribution and licensing notes are in [`assets/sounds/SOURCES.md`](assets/sounds/SOURCES.md).
