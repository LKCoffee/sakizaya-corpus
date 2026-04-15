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


# ──────────────────────────────────────────
# 3. 相似句搜尋（Jaccard token overlap）
# ──────────────────────────────────────────

def _tokenize(text: str) -> set:
    """
    把文字切成 token set，按空格 + 常見標點分割，過濾空字串。
    """
    parts = re.split(r"[\s\.,;:!?。，、；：！？「」『』【】()（）\-/]+", text.lower())
    return set(p for p in parts if p)


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

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT szy, zh FROM parallel")
        rows = cur.fetchall()
    finally:
        conn.close()

    scored = []
    compare_col = "zh" if lang == "zh" else "szy"
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
        print(f"  [{r['score']:.4f}] szy: {r['szy']} ↔ zh: {r['zh']}")

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
