# 撒奇萊雅語翻譯機 安裝說明

## Windows

1. 安裝 Python：https://python.org
   - 點「Download Python」，一路按「Next」
   - **安裝時記得勾選「Add Python to PATH」**
2. 安裝 Ollama（**只有 AI 版才需要**）：https://ollama.ai
   - 點「Download」，下載完執行安裝程式
3. 雙擊 `setup.bat`（會自動安裝套件並下載 AI 模型，等幾分鐘）
4. 安裝完成後：
   - **Lite 版**（快速，不需 AI）：雙擊 `start.bat`
   - **AI 版**（較慢，需要 Ollama）：雙擊 `start_ai.bat`

---

## Mac / Linux

1. 安裝 Python：https://python.org
   - 或用 Homebrew：`brew install python`
2. 安裝 Ollama（**只有 AI 版才需要**）：https://ollama.ai
3. 在終端機執行：
   ```bash
   sh setup.sh
   ```
4. 安裝完成後：
   - **Lite 版**：`sh start.sh`
   - **AI 版**：`sh start_ai.sh`

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
