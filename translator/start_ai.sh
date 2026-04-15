#!/usr/bin/env bash
echo "============================================"
echo " 撒奇萊雅語翻譯機（AI 版）啟動中..."
echo "============================================"
echo
echo "啟動 Ollama 服務..."
ollama serve &
sleep 3
echo "啟動撒奇萊雅語翻譯機（AI 版）..."
export SZY_DB=sakizaya.db
python3 app_ai.py
