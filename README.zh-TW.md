# NightyGo

[English](README.md) | 繁體中文

使用 PySide6 開發的圍棋對局、棋譜編輯與 AI 覆盤工作室。支援 SGF 變化樹、棋譜標記、在地棋譜庫、KataGo 即時分析和整盤覆盤；介面可切換深色／暖白主題，也提供 Qt Quick 棋盤工作區。

## 開發與啟動

本專案使用 uv 管理 PySide6 環境。在專案目錄執行：

```bash
uv sync --locked
uv run --locked python -m nightygo
```

程式會以時間、嚴重程度與模組名稱輸出標準 log。啟動前設定
`NIGHTYGO_LOG_LEVEL=DEBUG` 可顯示診斷細節。

## 功能

- 在 19×19 棋盤上落子與虛手，支援提子、自殺手判定與單劫規則。
- 落子前顯示半透明棋子預覽，並可選擇五組真實圍棋落子錄音。
- 可切換經典木紋、星空或夜空棋盤，以及傳統、星空或月岩棋子材質。
- 悔棋，並點選棋譜樹中的節點跳至局面或瀏覽變化分支。
- 匯入與匯出 SGF 棋譜集，保留註解與其他變化線。
- 編輯棋局資訊、棋步註解、主線／分支和棋盤上的三角形、方形、圓形、叉號、標籤、線與箭頭。
- 搜尋近期棋譜的棋手、賽事、結果和自訂標籤；未儲存棋局會提示並自動建立復原快照。
- 設定本機 KataGo 執行檔和參數，以非同步方式查看候選著、勝率、目差與 ownership；整盤覆盤可檢視勝率曲線並跳回重大波動棋步。
- 於「View → QML workspace preview」試用 Qt Quick 棋盤；「Settings → Preferences」可選深色／暖白主題、字級和星空背景動畫。

使用「File → Open SGF」開啟棋譜，使用「File → Save SGF」儲存。
AI 分析需要自行安裝 KataGo、下載相符模型，並在「Settings → Preferences」選擇執行檔及 GTP 參數；NightyGo 不會自動下載模型。Preferences 也可預聽落子音效、調整字級、主題、動畫與棋盤／棋子材質。所有設定會記住。
