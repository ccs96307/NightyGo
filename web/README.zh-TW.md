# NightyGo 網頁版

這是一個免安裝的瀏覽器版圍棋工作室，使用 HTML、CSS、JavaScript 與 KataGo WebAssembly。使用者不必安裝桌面程式；AI 模型由使用者自行下載，儲存在瀏覽器 IndexedDB，分析在本機瀏覽器執行。

## 本機啟動

在專案根目錄執行：

```bash
python3 -m http.server 8000 --directory web
```

接著開啟 `http://localhost:8000`。WebGPU 和離線快取需要 HTTPS 或 localhost；直接用 `file://` 開啟不支援完整功能。

## 目前具備

- 9、13、19 路棋盤，落子預覽、提子、禁自殺、單劫、虛手、雙方連續虛手結束。
- 悔棋、重做、前後步與點擊棋譜樹節點；主線保持垂直，變化只在分歧處分支。
- SGF FF[4] 棋譜樹匯入、匯出，支援同一檔案的多局集合，匯出時保留整個集合、分支與節點屬性。
- 編輯棋手、賽事、結果、貼目與目前節點註解。
- 瀏覽器本機棋譜收藏、搜尋、自動復原快照，以及離線快取。
- 深淺色、五種落子音效、四段提子音效、字級、棋盤材質、棋子材質和動畫偏好。
- 中、英、日、韓、簡體中文與繁體中文介面切換；少數次要狀態提示仍可能顯示英文。
- 可建立三角形、方形、圓形、叉號和文字標籤；線段與箭頭可顯示匯入的標記，但目前不能在網頁版新增。
- KataGo WebAssembly 模型載入、WebGPU/CPU 推論、候選著、勝率/目差、ownership 棋盤覆蓋、有限 visits 的 MCTS AI 落子和主線覆盤。
- AI Model Config 提供輕量、平衡、最新高強度官方模型下載入口，依瀏覽器回報記憶體給粗略建議；模型需下載後手動匯入，避免跨網域 CORS 限制，模型檔只存本機。
- WebGPU 偵測、裝置資訊提示、PWA 離線快取與 SGF parser 單元測試。

## 限制與尚未完成

目前 AI 以單執行緒瀏覽器 MCTS 為主，沒有 KataGo 桌面版多執行緒搜尋的速度；WebGPU 是否可用依瀏覽器、GPU 驅動與安全來源（HTTPS/localhost）而定，否則可能改用較慢的 CPU。首次模型下載由使用者從官方頁面完成，再從檔案選擇器匯入；瀏覽器無法直接跨來源讀取官方模型下載內容。記憶體建議是粗估，不代表保證能載入。AI 搜尋支援標準兩子以上黑棋讓子；不支援含 AW/AE 白棋初始設定或中途編輯盤面的 SGF 變化。整盤覆盤目前分析主線，最多 250 手。棋譜與設定儲存於目前瀏覽器；清除網站資料會移除收藏，請定期匯出 SGF 備份。

### 開發與測試

```bash
node --test web/tests/*.test.js
node --check web/app.js
```

瀏覽器 KataGo WASM 可用 `EMSDK_DIR=/path/to/emsdk bash scripts/build-web-engine.sh` 重建；需要 Emscripten 7.0.1、Eigen 3，以及網路連線下載 WebGPU build port。GitHub Pages workflow 會建置並部署靜態版。

引擎程式使用 MIT 授權，授權副本位於 [`assets/engine/UPSTREAM-LICENSE`](assets/engine/UPSTREAM-LICENSE)；KataGo 神經網路各自受其網路模型授權約束，請在官方模型頁確認。

音效沿用桌面版素材，來源及授權資訊見 [`../nightygo/assets/SOUND_SOURCES.md`](../nightygo/assets/SOUND_SOURCES.md)。
