# 撒奇萊雅語語料庫 & AI 翻譯工具組
### Sakizaya Language Corpus & AI Toolkit

> **全球第一個開放離線撒奇萊雅語語料庫**
> First open offline corpus for Sakizaya (szy) — UNESCO critically endangered, ~590 native speakers

[English](#english) | [中文](#中文)

---

<a name="中文"></a>
## 中文

### 背景

撒奇萊雅族（Sakizaya）是台灣原住民族之一，長期與阿美族混居，語言保存面臨嚴峻挑戰。
本語料庫目標：讓這門語言**永久保存**，任何人在**完全離線**環境下都能使用。

### 內容

| 項目 | 數量 | 說明 |
|------|------|------|
| 雙語句對（撒奇萊雅語 ↔ 中文）| 75,000+ | FormosanBank + szy.Wikipedia + ILRDF |
| 詞彙條目 | 6,000+ | 含詞性標記與例句 |
| `query.py` | — | 離線 CLI 查詢工具，無需網路 |
| `skills/sakizaya/` | — | Claude AI 雙向翻譯技能模組 |

### 快速開始

```bash
git clone https://github.com/LKCoffee/sakizaya-corpus.git
cd sakizaya-corpus
python query.py stats
python query.py word belih
```

### 資料來源

| 來源 | 授權 | 說明 |
|------|------|------|
| FormosanBank | CC BY-SA 4.0 | 中央研究院 |
| szy.Wikipedia | CC BY-SA 4.0 | 維基媒體基金會 |
| 原住民族語言研究發展基金會（ILRDF） | CC BY-NC 4.0 | 限非商業使用 |
| 社區文獻 | 見個別檔案 | 族人貢獻 |

### 引用格式

```
LKCoffee. (2026). 撒奇萊雅語語料庫 v1.0.0 [資料集].
https://github.com/LKCoffee/sakizaya-corpus
授權：CC BY-NC-SA 4.0
```

### 授權

本語料庫採用 **創用CC 姓名標示-非商業性-相同方式分享 4.0 國際（CC BY-NC-SA 4.0）** 授權釋出。

---

<a name="english"></a>
## English

### What's Included

| Component | Count | Description |
|-----------|-------|-------------|
| Parallel sentence pairs (Sakizaya ↔ Chinese) | 75,000+ | FormosanBank, szy.Wikipedia, ILRDF |
| Lexicon entries | 6,000+ | With POS tags and usage examples |
| `query.py` | — | Offline CLI query tool (no internet required) |
| `skills/sakizaya/` | — | Claude AI bidirectional translation skill |

### Quick Start

```bash
git clone https://github.com/LKCoffee/sakizaya-corpus.git
cd sakizaya-corpus
python query.py stats
python query.py word belih
```

### Data Sources

| Source | License | Notes |
|--------|---------|-------|
| FormosanBank | CC BY-SA 4.0 | Academia Sinica |
| szy.Wikipedia | CC BY-SA 4.0 | Wikimedia Foundation |
| ILRDF | CC BY-NC 4.0 | Non-commercial only |
| Local community documents | See individual files | Community contributed |

### Citation

```
LKCoffee. (2026). Sakizaya Corpus v1.0.0 [Data set].
https://github.com/LKCoffee/sakizaya-corpus
License: CC BY-NC-SA 4.0
```

### License

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**

Full license text: [LICENSE](LICENSE)
