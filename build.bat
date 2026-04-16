@echo off
chcp 65001 >nul
echo 撒奇萊雅語翻譯工具 - 建立 .exe
echo ===================================

:: 確認 PyInstaller 已安裝
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 安裝 PyInstaller...
    pip install pyinstaller
)

:: 清除舊的 build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: 打包
pyinstaller --onedir --windowed --name sakizaya-translator translator\app_tk.py --distpath dist --workpath build

if errorlevel 1 (
    echo.
    echo [錯誤] 打包失敗
    pause
    exit /b 1
)

:: 複製 DB（如果本地有）
if exist sakizaya.db (
    echo 複製資料庫...
    copy /y sakizaya.db dist\sakizaya-translator\sakizaya.db >nul
    echo 資料庫已複製
) else (
    echo.
    echo [注意] 找不到 sakizaya.db
    echo 請手動將 sakizaya.db 放到 dist\sakizaya-translator\ 資料夾
)

echo.
echo 完成：dist\sakizaya-translator\sakizaya-translator.exe
pause
