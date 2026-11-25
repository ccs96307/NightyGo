# NightyGo

[English](README.md) | 繁體中文

使用 PySide6 開發的圍棋記譜程式，支援落子預覽、落子音效、悔棋、SGF 匯入匯出與變化圖瀏覽。

## 開發與啟動

本專案使用 uv 管理 PySide6 環境。在專案目錄執行：

```bash
uv sync --locked
uv run python -m nightygo
```

## 功能

- 在 19×19 棋盤上落子與虛手，支援提子、自殺手判定與單劫規則。
- 落子前顯示半透明棋子預覽，落子時播放音效。
- 悔棋並瀏覽 SGF 棋譜中的變化分支。
- 匯入與匯出 SGF 棋譜集，保留註解與其他變化線。

使用「File → Open SGF」開啟棋譜，使用「File → Save SGF」儲存。
