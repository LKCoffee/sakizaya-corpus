@echo off
cd /d %~dp0
chcp 65001 >nul
echo ============================================
echo  Sakizaya Translator - AI Edition
echo ============================================
echo.

:: Check if AI translator is already running → just open browser
curl -s http://localhost:7861 >nul 2>&1
if not errorlevel 1 (
    echo AI Translator already running. Opening browser...
    start "" http://127.0.0.1:7861
    goto :eof
)

:: Check if Ollama is already running (avoid double-start)
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo Starting Ollama service...
    set OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe
    if exist "%OLLAMA_EXE%" (
        start "" "%OLLAMA_EXE%" serve
    ) else (
        start "" ollama serve
    )
    timeout /t 4 /nobreak >nul
) else (
    echo Ollama already running.
)

echo Starting AI Translator...
echo Browser will open at http://127.0.0.1:7861
echo.
set SZY_DB=%~dp0sakizaya.db
python "%~dp0app_ai.py"
if errorlevel 1 (
    echo.
    echo [Error] Launch failed. Check:
    echo   1. Run setup.bat first
    echo   2. Ollama installed, model downloaded: ollama pull qwen3.5
    echo   3. sakizaya.db exists in this folder
    pause
)
