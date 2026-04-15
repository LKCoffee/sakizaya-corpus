# Sakizaya Corpus — Repo Structure

---

## GitHub Repo 推薦結構

```
sakizaya-corpus/
├── README.md                  # 專案說明、快速開始、引用格式
├── LICENSE                    # CC BY 4.0（語料）/ MIT（程式碼）
├── .gitignore                 # 排除 *.db、*.xml、data/raw/
├── build_all.sh               # 一鍵建庫腳本
├── build_db.py                # FormosanBank XML → SQLite
├── extract_parallel.py        # Wikipedia dump → 平行語料（v1）
├── extract_parallel_v2.py     # 平行語料改良版（段落對齊）
├── import_ilrdf_xml.py        # ILRDF 辭典 XML → SQLite
├── build_lexicon.py           # 建立 lexicon CSV
├── query.py                   # 離線查詢 CLI
├── skills/
│   └── sakizaya/
│       ├── SKILL.md           # Claude AI 翻譯 skill 說明
│       └── references/        # 語料統計、詞性標記參考
├── data/
│   └── docx/                  # 三份本地語料（.docx，不含原始 XML）
└── notes/                     # 進度節點紀錄（非正式，開發日誌）
```

**注意：**
- `*.db`、`data/raw/`（FormosanBank XML、Wikipedia dump、ILRDF XML）不進 repo，由使用者自行準備或從 Release 下載預建 `.db`
- `skills/sakizaya/references/` 放語言學參考資料（焦點系統說明、詞性代碼表）

---

## HuggingFace Dataset 結構

```
sakizaya-corpus/
├── README.md                  # Dataset card（HF 格式，含 license/language/task_categories）
├── data/
│   ├── parallel/
│   │   ├── train.jsonl        # 平行句對（撒奇萊雅語 ↔ 中文）
│   │   └── metadata.json      # 來源、配對方法、誤配率估計
│   └── lexicon/
│       ├── lexicon.csv        # 詞典（word / pos / meaning_zh / example_szy / example_zh）
│       └── metadata.json      # ILRDF 來源說明、版本
```

**JSONL 欄位（parallel/train.jsonl）：**
```json
{
  "szy": "...",          // 撒奇萊雅語原文
  "zh": "...",           // 中文對應
  "source": "wikipedia", // 來源：wikipedia / formosanbank
  "confidence": 0.7      // 配對信心值（0–1，相鄰段落法為估算值）
}
```

---

## GitHub Release 附件清單

| 檔案 | 說明 | 大小估計 |
|------|------|----------|
| `sakizaya.db` | 預建 SQLite 資料庫（含全部語料 + 詞典） | ~50–80 MB |
| `lexicon.csv` | 獨立詞典 CSV（無需 SQLite） | ~2 MB |
| `parallel.csv` | 獨立平行語料 CSV（無需 SQLite） | ~15–25 MB |
| `build_all.sh` | 一鍵建庫腳本（source code） | < 1 KB |
| `sakizaya-corpus-v1.0.0.zip` | 完整 repo 快照（含所有 .py 腳本） | ~1 MB |

**下載優先序：**
1. 只要查詞 → `lexicon.csv`
2. 要做 NLP 研究 → `parallel.csv` + `lexicon.csv`
3. 要用 query.py 離線工具 → `sakizaya.db`
4. 要從頭 build → clone repo + 自備原始資料 + `bash build_all.sh`
