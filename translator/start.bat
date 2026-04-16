@echo off
cd /d %~dp0
chcp 65001 >nul

:: Check if translator is already running → just open browser
curl -s http://localhost:7860 >nul 2>&1
if not errorlevel 1 (
    echo Translator already running. Opening browser...
    start "" http://127.0.0.1:7860
    goto :eof
)

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

python -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo Installing Gradio, please wait...
    pip install gradio -q
    if errorlevel 1 (
        echo Gradio install failed. Check your internet connection.
        pause
        exit /b 1
    )
)

set SZY_DB=%~dp0..\sakizaya.db
echo Starting Sakizaya Translator...
echo Browser will open at http://127.0.0.1:7860
echo.
python "%~dp0app.py"
echo.
echo Press any key to close.
pause
