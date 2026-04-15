#!/usr/bin/env bash
set -e

echo "============================================"
echo " 撒奇萊雅語翻譯機 — 安裝程式（Mac/Linux）"
echo "============================================"
echo

# ── Step 1：檢查 Python ──────────────────────
echo "[1/5] 檢查 Python 是否已安裝..."
if ! command -v python3 &>/dev/null; then
    echo
    echo "[錯誤] 找不到 python3。"
    echo "請先安裝 Python 3.10 以上版本："
    echo "  https://python.org"
    echo "  或使用 Homebrew：brew install python"
    exit 1
fi
python3 --version
echo "Python 已就緒。"
echo

# ── Step 2：安裝 Python 套件 ─────────────────
echo "[2/5] 安裝所需 Python 套件（gradio、requests）..."
pip3 install gradio requests
echo "套件安裝完成。"
echo

# ── Step 3：檢查 Ollama（AI 版用） ───────────
echo "[3/5] 檢查 Ollama 是否已安裝..."
if ! command -v ollama &>/dev/null; then
    echo
    echo "[提示] 找不到 Ollama。"
    echo "若只使用「Lite 版」（start.sh），可略過此步驟。"
    echo "若要使用「AI 版」（start_ai.sh），請先安裝 Ollama："
    echo "  https://ollama.ai"
    echo
    echo "跳過 AI 模型下載，繼續安裝..."
    SKIP_OLLAMA=1
else
    ollama --version
    echo "Ollama 已就緒。"
    echo
fi

# ── Step 4：下載 AI 模型 ─────────────────────
if [ -z "$SKIP_OLLAMA" ]; then
    echo "[4/5] 正在下載 AI 模型（~1GB），請稍候..."
    echo "      這一步需要幾分鐘，請保持網路連線。"
    ollama pull qwen2.5:1.5b
    echo "AI 模型下載完成。"
    echo
else
    echo "[4/5] 跳過 AI 模型下載。"
    echo
fi

# ── Step 5：複製資料庫 ───────────────────────
echo "[5/5] 複製撒奇萊雅語資料庫..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../sakizaya.db" ]; then
    cp "$SCRIPT_DIR/../sakizaya.db" "$SCRIPT_DIR/sakizaya.db"
    echo "資料庫複製完成：sakizaya.db"
else
    echo "[警告] 找不到 ../sakizaya.db，請確認資料庫檔案位置。"
    echo "你可以手動將 sakizaya.db 放到本資料夾（translator/）中。"
fi
echo

# ── 完成 ─────────────────────────────────────
echo "============================================"
echo " 安裝完成！"
echo
echo " 啟動方式："
echo "   Lite 版（不需 AI）：sh start.sh"
echo "   AI  版（需要 Ollama）：sh start_ai.sh"
echo "============================================"
echo
