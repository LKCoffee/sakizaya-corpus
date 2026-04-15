@echo off
chcp 65001 >nul
echo ============================================
echo  撒奇萊雅語翻譯機（Lite 版）啟動中...
echo ============================================
echo.
set SZY_DB=sakizaya.db
python app.py
if errorlevel 1 (
    echo.
    echo [錯誤] 啟動失敗。請確認：
    echo   1. 已執行 setup.bat 完成安裝
    echo   2. sakizaya.db 存在於本資料夾
    pause
)
