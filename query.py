"""
Sakizaya 語料庫查詢工具（全離線）
用法：
  python query.py              → 互動模式
  python query.py word <詞>   → 查詞
  python query.py search <文字> → 搜例句
  python query.py stats        → 統計
"""

import sqlite3, sys, os
from pathlib import Path

DB = Path(r"C:\Users\User\sakizaya_corpus\sakizaya.db")

PARTICLES = {'a','ku','tu','nu','u','sa','i','ci','atu','sisa','caay','zayhan',
             'anu','hawsa','ancaay','han','haw','nida','kita','yaken','isu',
             'ciniza','kamen','yamu','ciniheni','baan','acaay','ka','pa','ma'}

# ── 詞根正規化 ───────────────────────────────────────────────────────────────
# 後綴優先長→短，避免 -hen 先被切掉變成 -en 再切
SUFFIXES = ['-en', '-an', '-ay']
PREFIXES = ['misa-', 'mu-', 'mi-', 'ma-', 'ka-', 'pa-']

def stem(word: str) -> str | None:
    """
    嘗試去掉撒奇萊雅語常見後綴和前綴，回傳詞根。
    若無法還原（詞太短或不符合任何規則）回傳 None。
    Examples:
      belihen → belih  (後綴 -en)
      mubelih → belih  (前綴 mu-)
      mufitik → fitik  (前綴 mu-)
    """
    w = word.lower()

    # 去後綴（優先長的）
    stripped = w
    for suf in SUFFIXES:
        actual_suf = suf.lstrip('-')
        if w.endswith(actual_suf) and len(w) - len(actual_suf) >= 3:
            stripped = w[: len(w) - len(actual_suf)]
            break

    # 去前綴（後綴已去除的結果再過一次）
    for pre in PREFIXES:
        actual_pre = pre.rstrip('-')
        if stripped.startswith(actual_pre) and len(stripped) - len(actual_pre) >= 3:
            return stripped[len(actual_pre):]

    # 只去了後綴（無前綴）
    if stripped != w:
        return stripped

    return None

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ── 查詞 ────────────────────────────────────────────────────────
def _lookup_core(cur, word, label=None):
    """
    對單一詞形查 lexicon + words + parallel，印出結果。
    label：若非 None，在標題行附加說明（如「詞根搜尋」）。
    回傳 True 若有找到任何結果（lexicon 或 parallel），否則 False。
    """
    header = f"\n【查詞】{word}"
    if label:
        header += f"  ← {label}"
    print(header)
    print("─" * 50)

    found_any = False

    # lexicon 表
    cur.execute("SELECT * FROM lexicon WHERE word = ? COLLATE NOCASE", (word,))
    lex = cur.fetchone()
    if lex:
        found_any = True
        print(f"  詞類：{lex['pos'] or '—'}")
        print(f"  中文：{lex['meaning_zh'] or '—'}")
        print(f"  信心：{lex['confidence'] or '—'}")
        print(f"  來源：{lex['source'] or '—'}")
        if lex['example_szy']:
            print(f"  例句：{lex['example_szy'][:100]}")
    else:
        print("  （詞典無收錄）")

    # 詞頻
    cur.execute("SELECT frequency FROM words WHERE word = ? COLLATE NOCASE", (word.lower(),))
    freq = cur.fetchone()
    if freq:
        print(f"  語料頻率：{freq[0]:,} 次")

    # 平行例句
    cur.execute("""
        SELECT szy, zh FROM parallel
        WHERE szy LIKE ? AND LENGTH(szy) < 300
        LIMIT 3
    """, (f'%{word}%',))
    rows = cur.fetchall()
    if rows:
        found_any = True
        print(f"\n  平行例句（{len(rows)} 筆）：")
        for i, r in enumerate(rows, 1):
            print(f"  {i}. szy: {r['szy'][:120]}")
            print(f"     zh:  {r['zh'][:120]}")
    else:
        print("  （無平行例句）")

    return found_any


def lookup_word(word):
    conn = get_conn()
    cur = conn.cursor()

    # 先查原形
    found = _lookup_core(cur, word)

    # 若原形無結果，嘗試詞根還原
    if not found:
        root = stem(word)
        if root and root.lower() != word.lower():
            print(f"\n  ── 原形無結果，嘗試詞根：{root} ──")
            _lookup_core(cur, root, label=f"搜尋詞根 {root}（原始輸入：{word}）")

    conn.close()

# ── 搜尋 ────────────────────────────────────────────────────────
def search(text):
    conn = get_conn()
    cur = conn.cursor()
    print(f"\n【搜尋】{text}")
    print("─" * 50)

    # 搜撒奇萊雅
    cur.execute("""
        SELECT article_title, szy, zh FROM parallel
        WHERE szy LIKE ? AND LENGTH(szy) < 400
        LIMIT 5
    """, (f'%{text}%',))
    rows = cur.fetchall()

    # 也搜中文
    if not rows:
        cur.execute("""
            SELECT article_title, szy, zh FROM parallel
            WHERE zh LIKE ? AND LENGTH(zh) < 400
            LIMIT 5
        """, (f'%{text}%',))
        rows = cur.fetchall()

    if rows:
        for i, r in enumerate(rows, 1):
            print(f"\n  [{r['article_title'][:30]}]")
            print(f"  szy: {r['szy'][:150]}")
            print(f"  zh:  {r['zh'][:150]}")
    else:
        print("  找不到結果")
    conn.close()

# ── 統計 ────────────────────────────────────────────────────────
def stats():
    conn = get_conn()
    cur = conn.cursor()
    print("\n【資料庫統計】")
    print("─" * 50)
    for label, sql in [
        ("文章數",    "SELECT COUNT(*) FROM articles"),
        ("句子數",    "SELECT COUNT(*) FROM sentences"),
        ("平行句對",  "SELECT COUNT(*) FROM parallel"),
        ("詞條數",    "SELECT COUNT(*) FROM words"),
    ]:
        cur.execute(sql)
        print(f"  {label}：{cur.fetchone()[0]:,}")

    # 平行來源分布
    print("\n  平行語料來源：")
    cur.execute("SELECT source, COUNT(*) as n FROM parallel GROUP BY source ORDER BY n DESC")
    for r in cur.fetchall():
        print(f"    {r[0]:<25} {r[1]:>8,}")

    # 詞典大小
    try:
        cur.execute("SELECT COUNT(*) FROM lexicon")
        print(f"\n  詞典收錄：{cur.fetchone()[0]:,} 詞")
    except:
        print("\n  詞典：尚未建立")

    # Top 20 內容詞
    print("\n  高頻內容詞 Top 20：")
    cur.execute("""
        SELECT word, frequency FROM words
        WHERE LENGTH(word) > 2
        ORDER BY frequency DESC LIMIT 20
    """)
    for r in cur.fetchall():
        if r['word'].lower() not in PARTICLES:
            print(f"    {r['word']:<25} {r['frequency']:>7,}")
    conn.close()

# ── 互動模式 ────────────────────────────────────────────────────
def interactive():
    print("Sakizaya 語料庫查詢（輸入詞彙或中文，quit 離開）")
    print("─" * 50)
    while True:
        try:
            q = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() in ('quit','exit','q'):
            break
        lookup_word(q)

# ── 主程式 ──────────────────────────────────────────────────────
if __name__ == '__main__':
    if not DB.exists():
        print(f"找不到資料庫：{DB}")
        sys.exit(1)

    args = sys.argv[1:]
    if not args:
        interactive()
    elif args[0] == 'stats':
        stats()
    elif args[0] == 'word' and len(args) > 1:
        lookup_word(' '.join(args[1:]))
    elif args[0] == 'search' and len(args) > 1:
        search(' '.join(args[1:]))
    else:
        print("用法：python query.py [word <詞> | search <文字> | stats]")
