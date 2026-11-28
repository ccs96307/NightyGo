# NightyGo

[English](README.md) | 繁體中文

使用 PySide6 開發的圍棋對局、棋譜編輯與 AI 覆盤工作室。支援 SGF 變化樹、棋譜標記、在地棋譜庫、KataGo 即時分析和整盤覆盤；介面可切換深色／暖白主題，也提供 Qt Quick 棋盤工作區。

[開啟網頁版](https://ccs96307.github.io/NightyGo/) 或閱讀[網頁版說明](web/README.zh-TW.md)。KataGo 直接在裝置上執行，安裝的模型保存在瀏覽器。

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
- 在「Settings → AI Model Center」一併設定 KataGo 引擎與模型；依可用 RAM／NVIDIA VRAM 推薦模型級別，並可下載模型及在 64 位元 Linux／Windows 安裝相容的官方 OpenCL 引擎。
- 使用 KataGo 非同步查看候選著、勝率、目差與 ownership；整盤覆盤可檢視勝率曲線並跳回重大波動棋步。
- 於「View → QML workspace preview」試用 Qt Quick 棋盤；「Settings → Preferences」可選深色／暖白主題、字級與動態效果強度（關閉／細緻／完整）。落子、提子、預覽和棋譜樹導覽都有短促且克制的轉場。

使用「File → Open SGF」開啟棋譜，使用「File → Save SGF」儲存。
AI 設定集中在 AI Model Center。選擇模型後按「下載引擎並完成 AI 設定」，即可在同一流程安裝官方引擎、下載並設為目前模型；也可在引擎區選擇既有執行檔並調整進階啟動參數。模型與自動安裝的引擎會存放於應用程式資料目錄。自動安裝目前支援 64 位元 Linux／Windows 的官方 OpenCL 套件；其他系統可指定既有 KataGo 執行檔。記憶體建議依可用 RAM／VRAM 和模型架構估算，實際需求也會受引擎後端和搜尋快取影響。Preferences 的字級、主題、動態效果、音效與材質會即時預覽；按「確定」才儲存，按「取消」會還原原設定。
可使用頂端工具列的語言選單，在 English、繁體中文、简体中文、日本語與 한국어 之間切換；選擇會自動記住。
