@echo off
chcp 65001 >nul
echo ============================================
echo  撒奇萊雅語翻譯機 — 安裝程式
echo ============================================
echo.

:: ── Step 1：檢查 Python ──────────────────────
echo [1/5] 檢查 Python 是否已安裝...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [錯誤] 找不到 Python。
    echo 請先安裝 Python 3.10 以上版本：
    echo   https://python.org
    echo.
    echo 安裝時請勾選「Add Python to PATH」選項。
    pause
    exit /b 1
)
python --version
python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [Error] Python 3.10 or above is required.
    echo Current version:
    python --version
    echo Please install Python 3.10+ from: https://python.org
    echo.
    pause
    exit /b 1
)
echo Python 已就緒。
echo.

:: ── Step 2：安裝 Python 套件 ─────────────────
echo [2/5] 安裝所需 Python 套件（gradio、requests）...
pip install gradio requests
if errorlevel 1 (
    echo.
    echo [錯誤] 套件安裝失敗，請確認網路連線後重試。
    pause
    exit /b 1
)
echo 套件安裝完成。
echo.

:: ── Step 3：檢查 Ollama（AI 版用） ───────────
echo [3/5] 檢查 Ollama 是否已安裝...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [提示] 找不到 Ollama。
    echo 若只使用「Lite 版」（start.bat），可略過此步驟。
    echo 若要使用「AI 版」（start_ai.bat），請先安裝 Ollama：
    echo   https://ollama.ai
    echo.
    echo 如已確認只使用 Lite 版，按任意鍵繼續（跳過 AI 模型下載）...
    pause
    goto COPY_DB
)
ollama --version
echo Ollama 已就緒。
echo.

:: ── Step 4：下載 AI 模型 ─────────────────────
echo [4/5] 正在下載 AI 模型（~1GB），請稍候...
echo       這一步需要幾分鐘，請保持網路連線。
ollama pull qwen2.5:1.5b
if errorlevel 1 (
    echo.
    echo [警告] 模型下載失敗。AI 版功能將無法使用。
    echo 可稍後手動執行：ollama pull qwen2.5:1.5b
    echo.
)
echo AI 模型下載完成。
echo.

:: ── Step 5：複製資料庫 ───────────────────────
:COPY_DB
echo [5/5] 複製撒奇萊雅語資料庫...
if exist ..\sakizaya.db (
    copy /Y ..\sakizaya.db .\sakizaya.db >nul
    echo 資料庫複製完成：sakizaya.db
) else (
    echo [警告] 找不到 ..\sakizaya.db，請確認資料庫檔案位置。
    echo 你可以手動將 sakizaya.db 放到本資料夾（translator\）中。
)
echo.

:: ── 完成 ─────────────────────────────────────
echo ============================================
echo  安裝完成！
echo.
echo  啟動方式：
echo    Lite 版（不需 AI）：雙擊 start.bat
echo    AI  版（需要 Ollama）：雙擊 start_ai.bat
echo ============================================
echo.
pause
