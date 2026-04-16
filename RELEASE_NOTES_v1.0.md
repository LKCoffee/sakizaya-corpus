# Sakizaya Corpus — Release Notes v1.0.0

**Version:** v1.0.0
**Release Date:** 2026-04-15

---

## 亮點

- **首個開放撒奇萊雅語離線語料庫**
  撒奇萊雅語（Sakizaya）為台灣原住民族語之一，本專案為其首個可離線使用的開放語料庫。

- **90,471 平行句對（撒奇萊雅語 ↔ 中文）**
  來源：FormosanBank 語料 + 撒奇萊雅語 Wikipedia dump（szy.wikipedia.org）+ ALR 朗聲四起平台 + 本地文件 / 母語人士。

- **6,173 詞條（含 ILRDF 辭典例句）**
  整合原住民族語言研究發展基金會（ILRDF）離線 XML 詞典，含詞性標記與原始例句。

- **5,363 篇 Sakizaya Wikipedia 單語文本**（在 `sakizaya.db` 的 `articles` + `sentences` 表）
  來源：FormosanBank Sakizaya Wikipedia XML 語料，經正字法品質處理（CC BY-SA 4.0）。

- **離線查詢工具 `query.py`**
  支援中文關鍵字查詞、撒奇萊雅語全文搜尋、統計摘要。無需網路連線。

- **Claude AI 翻譯 skill**
  整合 `skills/sakizaya/` 翻譯腳本，支援雙向翻譯（中文 ↔ 撒奇萊雅語）、語言鑑別（自動區分阿美語混用）。

---

## 下載說明

### 直接用（推薦）
下載 `sakizaya.db`（預建 SQLite 資料庫），無需自行 build：

```bash
python query.py stats          # 查看統計
python query.py word 水        # 查詞（中文）
python query.py search malafi  # 搜尋（撒奇萊雅語）
```

### 自己 build
需事先準備離線原始資料（FormosanBank XML、Wikipedia dump、ILRDF XML）：

```bash
git clone https://github.com/LKCoffee/sakizaya-corpus
cd sakizaya-corpus
bash build_all.sh
```

詳見 `README.md` 的「資料來源準備」章節。

---

## 已知限制

| 項目 | 說明 |
|------|------|
| 平行語料誤配率 | 估計 30–40%。採相鄰段落配對法（Wikipedia），非對齊語料，研究使用需人工複核高頻詞對 |
| 詞典 meaning_zh 部分為空 | ILRDF XML 部分詞條缺中文釋義，待 M2 人工補完 |
| 動詞 BV 焦點例句待驗證 | 受事焦點（BV）例句來自語料自動抽取，尚未經母語人士語法性驗證 |

---

## 引用格式（APA）

> LKCoffee. (2026). *Sakizaya Corpus v1.0.0* [Data set]. GitHub.
> https://github.com/LKCoffee/sakizaya-corpus

---

## 感謝

- **FormosanBank**（NTU Linguistics + Boston College + MGH IHP 跨國合作）：提供 Sakizaya Wikipedia XML 語料（5,363 篇，CC BY-SA 4.0）
- **ILRDF 原住民族語言研究發展基金會**：提供撒奇萊雅語辭典 XML（6,173 詞條，CC BY-NC 4.0）
- **撒奇萊雅語 Wikipedia 貢獻者**（szy.wikipedia.org，Wikimedia Foundation）：提供自由授權的平行語料來源（CC BY-SA 4.0）
- **ALR 朗聲四起平台**（政大原住民族研究中心維護）：215 對全國語文競賽撒奇萊雅語朗讀文章平行句對
- **本地文件與母語人士**：補充語料與例句
