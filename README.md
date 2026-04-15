# Sakizaya Language Corpus & AI Toolkit

> First open offline corpus for Sakizaya (szy) — a critically endangered Austronesian language (~590 native speakers, UNESCO Red Book)

---

## What's Included

| Component | Description |
|---|---|
| 70,000+ parallel sentence pairs | Sakizaya ↔ Chinese, sourced from FormosanBank, szy.Wikipedia, ILRDF |
| 6,000+ lexicon entries | With part-of-speech tags and usage examples |
| `query.py` | Offline CLI query tool (no internet required) |
| `skills/sakizaya/` | Claude AI skill for bidirectional translation |

## Quick Start

```bash
git clone https://github.com/LKCoffee/sakizaya_corpus.git
python query.py stats
python query.py word belih
```

## Data Sources

| Source | License | Notes |
|---|---|---|
| FormosanBank | CC BY-SA 4.0 | Academia Sinica |
| szy.Wikipedia | CC BY-SA 4.0 | Wikimedia Foundation |
| ILRDF (原住民族語言研究發展基金會) | CC BY-NC 4.0 | Non-commercial use only |
| Local community documents | See individual files | Contributed by community members |

## Citation

If you use this corpus in research or applications, please cite:

```
Sakizaya Language Corpus & AI Toolkit (2025).
Contributors of the Sakizaya Corpus Project.
Available at: https://github.com/LKCoffee/sakizaya_corpus
License: CC BY-NC-SA 4.0
```

## License

This corpus is released under **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**.

You are free to share and adapt the material for non-commercial purposes, provided you give appropriate credit and distribute your contributions under the same license.

Full license text: [LICENSE](LICENSE)

---

# 撒奇萊雅語語料庫 & AI 翻譯工具組

> 全球第一個針對撒奇萊雅語（szy）的開放離線語料庫——UNESCO 極度瀕危語言，全球約 590 名母語者

---

## 背景

撒奇萊雅族（Sakizaya）是台灣原住民族之一，長期與阿美族混居，語言保存面臨嚴峻挑戰。本語料庫是全球第一個針對撒奇萊雅語的開放離線語料庫，目標是讓這門語言得以**永久保存**，並讓任何人在**完全離線**的環境下都能使用。

## 內容

| 項目 | 說明 |
|---|---|
| 70,000+ 雙語句對 | 撒奇萊雅語 ↔ 中文，來自 FormosanBank、szy.Wikipedia、ILRDF |
| 6,000+ 詞彙條目 | 含詞性標記與例句 |
| `query.py` | 離線 CLI 查詢工具，無需網路 |
| `skills/sakizaya/` | Claude AI 雙向翻譯技能模組 |

## 快速開始

```bash
git clone https://github.com/LKCoffee/sakizaya_corpus.git
python query.py stats
python query.py word belih
```

## 資料來源

| 來源 | 授權 | 說明 |
|---|---|---|
| FormosanBank | CC BY-SA 4.0 | 中央研究院 |
| szy.Wikipedia | CC BY-SA 4.0 | 維基媒體基金會 |
| 原住民族語言研究發展基金會（ILRDF） | CC BY-NC 4.0 | 限非商業使用 |
| 社區文獻 | 見個別檔案 | 族人貢獻 |

## 引用格式

```
撒奇萊雅語語料庫 & AI 翻譯工具組（2025）。
撒奇萊雅語料庫貢獻者。
https://github.com/LKCoffee/sakizaya_corpus
授權：CC BY-NC-SA 4.0
```

## 授權

本語料庫採用 **創用CC 姓名標示-非商業性-相同方式分享 4.0 國際（CC BY-NC-SA 4.0）** 授權釋出。

您可以在非商業目的下自由分享與改作本素材，但須標示來源，且衍生作品須採用相同授權。

完整授權文字：[LICENSE](LICENSE)
