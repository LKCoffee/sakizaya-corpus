# 撒奇萊雅語翻譯機 安裝說明

> **Windows 用戶只需要這幾個檔案（`.sh` 是 Mac/Linux 用的，忽略即可）：**
> - `setup.bat` — 第一次使用前先執行一次
> - `start.bat` — 啟動 **Lite 版**（字典查詢）
> - `start_ai.bat` — 啟動 **AI 版**（需要 Ollama）

> **Lite 版**：純字典查詢，不需 Ollama，任何電腦都能跑。
> **AI 版**：需要安裝 Ollama（免費，本機執行，不需要網路 API）。

## Windows

### Lite 版（推薦新手）

1. 安裝 Python：https://python.org
   - 點「Download Python」，一路按「Next」
   - **安裝時記得勾選「Add Python to PATH」**
2. 雙擊 `setup.bat`（會自動安裝所需套件）
3. 安裝完成後雙擊 `start.bat`

### AI 版（需要額外安裝 Ollama）

1. 安裝 Python（同上）
2. 安裝 Ollama：https://ollama.ai
   - 點「Download」→ 下載 Windows 安裝程式 → 執行 → 一路 Next
   - 安裝完成後 Ollama 會自動在背景執行（系統匣右下角有圖示）
   - **安裝完不需要手動啟動**，它會自己跑
3. 雙擊 `setup.bat`（會自動下載 AI 模型，**約 7GB**，視網速可能需要 20~60 分鐘）
4. 安裝完成後雙擊 `start_ai.bat`

---

## Mac / Linux

### Lite 版

1. 安裝 Python：https://python.org（或 `brew install python`）
2. 在終端機執行：`sh setup.sh`
3. 完成後：`sh start.sh`

### AI 版

1. 安裝 Python（同上）
2. 安裝 Ollama：
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
   安裝後 Ollama 會在背景執行，不需要手動啟動。
3. 執行 `sh setup.sh`（會自動下載 AI 模型）
4. 完成後：`sh start_ai.sh`

---

## 常見問題

**「'python' 不是內部或外部命令」**
Python 沒裝，或安裝時沒有勾「Add Python to PATH」。重裝一次，記得勾那個選項。

**「'ollama' 不是內部或外部命令」**
Ollama 沒裝。只有 AI 版才需要，Lite 版可以不管這個錯誤。

**「找不到 sakizaya.db」**
資料庫檔案沒有複製過來。手動把 `sakizaya.db` 放到 `translator/` 資料夾裡。

**翻譯速度很慢**
正常現象。AI 模型在你的電腦本機執行，速度依機器效能而定。

**畫面沒有自動打開**
程式啟動後會顯示網址（通常是 `http://127.0.0.1:7860`），手動複製到瀏覽器開啟。
