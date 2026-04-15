# 撒奇萊雅語翻譯機（AI 版）

中文 ↔ 撒奇萊雅語，Ollama LLM + 語料庫 RAG 加持。

---

## 系統需求

| 項目 | 最低需求 | 建議 |
|------|----------|------|
| RAM  | 4 GB     | 8 GB+（模型 + Gradio + 向量索引同時跑） |
| 磁碟 | 2 GB     | 5 GB+（Ollama 模型 + 語料庫） |
| OS   | Windows 10 / macOS 12 / Ubuntu 20.04 | — |
| Python | 3.10+ | 3.11+ |
| Ollama | 0.3.0+ | 最新版 |

---

## 安裝步驟

### Windows（setup.bat）

```bat
REM 1. 安裝 Ollama（官網下載）
REM    https://ollama.com/download/windows

REM 2. 下載翻譯模型
ollama pull qwen2.5:1.5b

REM 3. 安裝 Python 依賴
pip install gradio requests sentence-transformers numpy

REM 4. 建立語料庫索引（若尚未建立）
python build_db.py

REM 5. 啟動 Ollama（背景執行）
start /B ollama serve

REM 6. 啟動 AI 翻譯介面
python app_ai.py
```

### macOS / Linux（setup.sh）

```bash
#!/bin/bash
# 1. 安裝 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 下載翻譯模型
ollama pull qwen2.5:1.5b

# 3. 安裝 Python 依賴
pip install gradio requests sentence-transformers numpy

# 4. 建立語料庫索引（若尚未建立）
python build_db.py

# 5. 啟動 Ollama（背景執行）
ollama serve &

# 6. 啟動 AI 翻譯介面
python app_ai.py
```

---

## 使用說明

1. 確認 Ollama 已啟動（介面右下角顯示「✅ 已連線」）。
2. 在輸入框貼入中文或撒奇萊雅語文字（支援多句或整段文章）。
3. 點擊「翻譯」按鈕或按 Enter。
4. 主輸出框顯示 LLM 翻譯結果。
5. 展開「參考例句（RAG 來源）」區塊可查看最相關的語料庫例句。

### 語言方向

- 自動偵測：輸入中文→輸出撒奇萊雅語；輸入撒奇萊雅語→輸出中文。
- 偵測基於字元特徵（漢字比例、撒奇萊雅語詞彙辨識），混合語料以主體語言為準。

### 埠號

- 預設：`http://localhost:7861`
- Lite 版（app.py）預設為 7860，兩者可同時跑。

---

## 架構說明

```
app_ai.py                  ← Gradio UI（本檔）
├── translate.py           ← RAG 查詢層（detect_lang / find_similar / split_sentences）
│   └── sakizaya.db        ← SQLite 語料庫
└── ollama_translate.py    ← LLM 翻譯層（Ollama API）
    └── Ollama (本機)      ← qwen2.5:1.5b（或其他模型）
```

---

## 已知限制

### 翻譯品質

- 翻譯品質受語料庫覆蓋率直接影響。語料庫中無對應例句的詞彙，LLM 可能產生錯誤或臆測翻譯。
- 生僻詞、地名、人名、現代詞彙（如科技術語）可能翻錯或保留原文未翻譯。
- 撒奇萊雅語有多種方言差異，語料庫目前以書面標準語為主，口語變體覆蓋有限。
- 長篇文章（>500 字）受模型 context 視窗限制，後半段翻譯品質可能下降。

### 技術限制

- Ollama 必須在本機執行，不支援遠端 API（設計上為離線優先）。
- 模型首次載入需要 10–30 秒，請耐心等待。
- Windows 上 Ollama 若使用 CPU 推理，翻譯速度約 5–30 秒/句，視硬體而定。
- 語料庫索引（向量搜尋）在 RAM < 4 GB 的機器上可能觸發 swap，速度顯著下降。

### 不建議使用場景

- 法律文件、醫療文件等高正確性要求場合，請對照人工審核。
- 撒奇萊雅語←→阿美語混用文本的辨別，目前語言偵測準確率約 80%。

---

## 版本紀錄

| 版本 | 日期 | 說明 |
|------|------|------|
| AI v1.0 | 2026-04-15 | 初始版本，Ollama + RAG 整合 |

---

## 相關檔案

- `app.py` — Lite 版（純 RAG，無 LLM）
- `translate.py` — 核心查詢邏輯
- `ollama_translate.py` — Ollama 整合層
- `build_db.py` — 語料庫索引建立工具
