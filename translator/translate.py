"""
translate.py — 撒奇萊雅語翻譯工具核心引擎
Lite + AI 版共用。只使用標準庫（sqlite3、re）。
"""

import sqlite3
import re


# ──────────────────────────────────────────
# 1. 語言偵測
# ──────────────────────────────────────────

def detect_lang(text: str) -> str:
    """
    回傳 'zh' 或 'szy'。
    判斷方法：中文字符（CJK Unified Ideographs）佔比 > 30% → 中文。
    """
    if not text:
        return "szy"
    chinese_chars = re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]", text)
    ratio = len(chinese_chars) / len(text)
    return "zh" if ratio > 0.30 else "szy"


# ──────────────────────────────────────────
# 2. 詞典查詢
# ──────────────────────────────────────────

def lookup_word(db_path: str, word: str) -> dict:
    """
    從 lexicon 表查詢單詞。
    回傳 dict：{word, meaning_zh, example_szy, example_zh}
    找不到時回傳空 dict。
    大小寫不敏感（COLLATE NOCASE）。
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT word, meaning_zh, example_szy, example_zh
            FROM lexicon
            WHERE word = ? COLLATE NOCASE
            LIMIT 1
            """,
            (word,),
        )
        row = cur.fetchone()
        if row:
            return dict(row)
        return {}
    finally:
        conn.close()


def lookup_words_in_text(db_path: str, text: str) -> list[dict]:
    """
    把文章拆成 token，逐一查 lexicon，回傳有命中的詞列表。
    適合撒奇萊雅語輸入（按 word 欄位查）。
    """
    tokens = _tokenize(text)
    results = []
    seen = set()
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        entry = lookup_word(db_path, token)
        if entry:
            results.append(entry)
    return results


def lookup_by_meaning(db_path: str, text: str) -> list[dict]:
    """
    從 lexicon 表按 meaning_zh 反查（中文 → 撒奇萊雅語方向）。
    優先回傳「定義命中」（meaning_zh 不含 [例] 前綴），
    僅在無定義命中時才 fallback 到「例句命中」並加 _match_type 標記。
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        direct = []   # meaning_zh 是真正定義（不含 [例]）
        example = []  # meaning_zh 只是例句
        seen = set()

        for token in _tokenize(text):
            if not token:
                continue

            # 精確比對
            cur.execute(
                """
                SELECT word, meaning_zh, example_szy, example_zh
                FROM lexicon
                WHERE meaning_zh = ? COLLATE NOCASE
                LIMIT 3
                """,
                (token,),
            )
            for row in cur.fetchall():
                if row["word"] not in seen:
                    seen.add(row["word"])
                    d = dict(row)
                    d["_match_type"] = "direct"
                    direct.append(d)

            # 模糊比對（含 [例] 與不含 [例] 分開）
            cur.execute(
                """
                SELECT word, meaning_zh, example_szy, example_zh
                FROM lexicon
                WHERE meaning_zh LIKE ? COLLATE NOCASE
                LIMIT 10
                """,
                (f"%{token}%",),
            )
            for row in cur.fetchall():
                if row["word"] not in seen:
                    seen.add(row["word"])
                    d = dict(row)
                    mz = (row["meaning_zh"] or "")
                    if mz.startswith("[例]") or mz.startswith("【例】"):
                        d["_match_type"] = "example"
                        example.append(d)
                    else:
                        d["_match_type"] = "direct"
                        direct.append(d)

        # 有定義命中就只回定義；否則回例句命中（上限 5）
        if direct:
            return direct[:10]
        return example[:5]
    finally:
        conn.close()


# ──────────────────────────────────────────
# 3. 相似句搜尋（Jaccard token overlap）
# ──────────────────────────────────────────

def _tokenize(text: str) -> set:
    """
    把文字切成 token set，按空格 + 常見標點分割，過濾空字串。
    對於多字 CJK token（如「這座山有很多的山豬」），額外展開成個別漢字，
    讓單字中文查詢（如「豬」）能命中包含該字的長句。
    """
    _CJK = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
    parts = re.split(r"[\s\.,;:!?。，、；：！？「」『』【】()（）\-/]+", text.lower())
    tokens = set(p for p in parts if p)
    # 展開多字 CJK token → 加入個別漢字
    extra = set()
    for t in tokens:
        if len(t) >= 2 and _CJK.search(t):
            extra.update(c for c in t if _CJK.match(c))
    return tokens | extra


def _jaccard(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def find_similar(
    db_path: str,
    text: str,
    lang: str,
    top_k: int = 5,
) -> list[dict]:
    """
    從 parallel 表用 Jaccard token overlap 找最相似的 top_k 句對。

    Parameters
    ----------
    db_path : str
    text    : str   — 查詢文字
    lang    : str   — 'zh' 或 'szy'，決定比對 parallel 表的哪個欄位
    top_k   : int

    Returns
    -------
    list of dict：[{szy, zh, score}, ...]，依 score 降序
    """
    query_tokens = _tokenize(text)

    compare_col = "zh" if lang == "zh" else "szy"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        # Performance: pre-filter rows containing at least one query token.
        # CJK single chars are meaningful → include them; skip short Latin tokens (particles).
        _CJK = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
        long_tokens = [t for t in query_tokens if len(t) >= 2 or _CJK.search(t)]
        if long_tokens and len(long_tokens) <= 6:
            conds = " OR ".join([f"{compare_col} LIKE ?" for _ in long_tokens])
            params = [f"%{t}%" for t in long_tokens]
            cur.execute(
                f"SELECT szy, zh FROM parallel WHERE {conds} AND LENGTH(szy) >= 15 AND LENGTH(zh) >= 5 AND szy NOT LIKE '%http%' AND zh NOT LIKE '%http%' LIMIT 2000", params
            )
        else:
            cur.execute("SELECT szy, zh FROM parallel WHERE LENGTH(szy) >= 15 AND LENGTH(zh) >= 5 AND szy NOT LIKE '%http%' AND zh NOT LIKE '%http%' LIMIT 5000")
        rows = cur.fetchall()
    finally:
        conn.close()

    scored = []
    for row in rows:
        corpus_text = row[compare_col] or ""
        corpus_tokens = _tokenize(corpus_text)
        score = _jaccard(query_tokens, corpus_tokens)
        scored.append({"szy": row["szy"], "zh": row["zh"], "score": round(score, 4)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


# ──────────────────────────────────────────
# 4. 文章分句
# ──────────────────────────────────────────

def split_sentences(text: str) -> list[str]:
    """
    按句號（中英文）、換行符拆句，過濾空字串。
    """
    parts = re.split(r"[。\.\n]+", text)
    return [p.strip() for p in parts if p.strip()]


def classify_query_type(text: str) -> str:
    """
    估計查詢詞的語言類型，用於顯示適當的無結果提示。
    回傳 'modern'、'abstract' 或 'traditional'。
    """
    modern_markers = re.compile(
        r"(電腦|手機|網路|網站|電視|汽車|飛機|機車|捷運|高鐵|冷氣|冰箱|"
        r"洗衣機|微波爐|相機|印表機|耳機|充電|電池|電梯|"
        r"臉書|youtube|ig|line|tiktok|google|app|ai|"
        r"人工智慧|機器人|雲端|程式|軟體|區塊鏈|加密貨幣|"
        r"超市|便利商店|網購|外送|信用卡|提款機|"
        r"醫院|疫苗|口罩|隔離|確診|pcr|"
        r"選舉|民主|環保|氣候變遷|碳排放|"
        r"電競|netflix|動漫|手遊|網紅|youtuber)",
        re.IGNORECASE,
    )
    abstract_markers = re.compile(
        r"(自由|平等|正義|民主|哲學|倫理|道德|邏輯|"
        r"存在|本質|意識|理性|感性|客觀|主觀|"
        r"宇宙|永恆|無限|意義|目的)"
    )
    if modern_markers.search(text):
        return "modern"
    if abstract_markers.search(text):
        return "abstract"
    return "traditional"


def gather_rag_examples(
    db_path: str,
    text: str,
    lang: str,
    top_k: int = 5,
    min_score: float = 0.05,
) -> list[dict]:
    """
    切句 → 逐句 find_similar → 去重 → 取 top_k。
    Lite 版（app.py）和 AI 版（app_ai.py）共用。
    """
    sentences = [s for s in split_sentences(text) if s.strip()]
    if not sentences:
        return []

    per_k = top_k if len(sentences) == 1 else 3
    seen: set = set()
    hits: list[dict] = []

    for sent in sentences[:8]:
        for r in find_similar(db_path, sent, lang=lang, top_k=per_k):
            key = (r.get("szy", ""), r.get("zh", ""))
            if key not in seen and r.get("score", 0) >= min_score:
                seen.add(key)
                hits.append(r)
        if len(hits) >= top_k * 2:
            break

    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits[:top_k]


# ──────────────────────────────────────────
# 簡易 CLI（直接執行時用）
# ──────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import os

    DB_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "sakizaya.db")
    db = os.environ.get("SZY_DB", DB_DEFAULT)

    if len(sys.argv) < 2:
        print("用法: python translate.py <查詢文字>")
        sys.exit(0)

    query = " ".join(sys.argv[1:])
    lang = detect_lang(query)
    print(f"偵測語言：{lang}")

    print("\n── 相似例句 ──")
    for r in find_similar(db, query, lang, top_k=5):
        print(f"  [{r['score']:.4f}] szy: {r['szy']} <-> zh: {r['zh']}")

    print("\n── 詞典查詢 ──")
    entry = lookup_word(db, query.strip())
    if entry:
        print(f"  {entry}")
    else:
        hits = lookup_words_in_text(db, query)
        if hits:
            for h in hits:
                print(f"  {h['word']} → {h['meaning_zh']}")
        else:
            print("  （無命中）")
