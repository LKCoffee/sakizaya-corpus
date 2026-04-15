@echo off
chcp 65001 >nul
echo ============================================
echo  撒奇萊雅語翻譯機（AI 版）啟動中...
echo ============================================
echo.
echo 啟動 Ollama 服務...
start "" ollama serve
timeout /t 3 /nobreak >nul
echo 啟動撒奇萊雅語翻譯機（AI 版）...
set SZY_DB=sakizaya.db
python app_ai.py
if errorlevel 1 (
    echo.
    echo [錯誤] 啟動失敗。請確認：
    echo   1. 已執行 setup.bat 完成安裝
    echo   2. Ollama 已安裝且模型已下載（qwen2.5:1.5b）
    echo   3. sakizaya.db 存在於本資料夾
    pause
)
