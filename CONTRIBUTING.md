# 如何貢獻 / How to Contribute

感謝你的關注。撒奇萊雅語（Sakizaya）是 UNESCO 列為極度瀕危的語言，每一筆貢獻都有意義。

---

## 三類貢獻者 / Three Ways to Help

### 1. 母語人士 / 族人

最直接、最珍貴的貢獻。你不需要懂程式，也不需要懂 Git。

**補充詞義**
1. 下載 `data/missing_words.csv`
2. 在 `meaning_zh` 欄填上中文詞義（一行一個詞）
3. 送 PR，或直接發 issue 把內容貼進去，我們幫你整理

**糾正翻譯錯誤**
發現翻譯不對、語境不對，開一個 issue，說明哪個詞、錯在哪裡、正確的用法是什麼。

**提供例句**
例句比定義更有用。歡迎提供日常對話句，附上中文意思。

---

### 2. 語言學家 / 研究者 / Linguists & Researchers

**驗證語法分析**
`data/` 下的語料含詞性標記（POS）與語法結構標注，如有錯誤歡迎指出。

**補充 BV 焦點例句**
撒奇萊雅語的焦點系統（Actor Focus / Patient Focus / Benefactive Focus / Locative Focus）是核心語法。缺例句的焦點類型記錄在 `data/focus_gaps.md`。

**改善語言鑑別**
撒奇萊雅語與阿美語高度相似，`classifier/` 模組負責自動鑑別，歡迎提出誤判案例或改善方案。

---

### 3. 技術貢獻者 / Technical Contributors

- **翻譯引擎改善**：`translator/` 資料夾，接受 PR
- **詞根分析（stem()）**：`query.py` 的 `stem()` 函式目前基於規則，歡迎改善或提供語料支援
- **Bug 修復**：發現問題開 issue，或直接送 PR
- **離線工具改善**：`query.py` CLI 介面、效能、跨平台相容性

技術環境：Python 3.9+，無框架依賴，核心是純字典查詢。

---

## 流程說明

```
issue → 討論 → PR → review → merge
```

- **Issue 優先**：不確定的改動先開 issue 討論
- **PR 歡迎**：小修直接送，不需要事先問
- 沒有 Git 也沒關係——把內容貼進 issue，我們幫你整理進去

---

## 授權說明 / License

貢獻的內容（包含詞彙、例句、翻譯修正）視同以 **CC BY-NC-SA 4.0** 授權釋出，與本語料庫主授權一致。

詳見 [LICENSE](LICENSE)。

---

## 聯絡

有任何疑問，開 issue 是最快的方式。

謝謝你。
