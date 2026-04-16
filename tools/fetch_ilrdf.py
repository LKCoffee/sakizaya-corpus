"""
fetch_ilrdf.py
批次從 ILRDF 查詢撒奇萊雅語詞義，補進 lexicon 表。

用法：
  python fetch_ilrdf.py           → 查所有 ★☆☆ 且 meaning_zh IS NULL
  python fetch_ilrdf.py --dry-run → 只印不寫入
  python fetch_ilrdf.py --limit N → 只處理前 N 個詞
  python fetch_ilrdf.py --infer-pos-only → 只跑 pos 推論（不呼叫 API）

API 來源：
  POST https://e-dictionary.ilrdf.org.tw/wsReDictionary.htm
  參數：FMT=1, account=E202403005, TribesCode=43, qw=<詞>
  Sakizaya tribe code = 43

不要自行執行——等老K確認 HTML/API 結構後再跑。
"""

import sqlite3
import requests
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime

# ── 設定 ────────────────────────────────────────────────────────────────────
DB      = Path(r"C:\Users\User\sakizaya_corpus\sakizaya.db")
LOG     = Path(r"C:\Users\User\sakizaya_corpus\fetch_ilrdf.log")
API_URL = "https://e-dictionary.ilrdf.org.tw/wsReDictionary.htm"

# Sakizaya tribe code（參考 formosanbank/Corpora/ILRDF_Dicts/CodeAndDocs/scrape.py 第 43 行）
TRIBE_CODE = 43

# API 帳號（同上腳本 line 42）
ACCOUNT = "E202403005"

# Rate limit：每次請求後暫停秒數
SLEEP_SEC = 2.0

# ── Logging 設定 ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


# ── API 查詢 ─────────────────────────────────────────────────────────────────
def query_ilrdf(word: str) -> list | None:
    """
    呼叫 ILRDF POST API，回傳 DATA list 或 None（失敗/無結果）。

    實際回傳格式（2026-04-16 確認）：
      {
        "GenericData": {
          "Message": {"status": "0", "content": "搜尋成功", "Count": "1"},
          "DATA": {
            "Name": "belih",
            "Frequency": "4",
            "Explanation": {"chinese": "翻臉；翻腮"},
            "Note": ""
          }
        }
      }
      DATA 是 dict（單筆）或 list（多筆），需兩者都處理。
      找不到時 Count="0"，DATA 為 null 或空。
    """
    import urllib.request, urllib.parse
    data = urllib.parse.urlencode({
        "FMT": 1,
        "account": ACCOUNT,
        "TribesCode": TRIBE_CODE,
        "qw": word,
    }).encode()
    try:
        req = urllib.request.Request(API_URL, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8', errors='replace')
        parsed = json.loads(body)
        result = parsed.get("GenericData", {}).get("DATA")
        if not result:
            return None
        # DATA 可能是 dict（單筆）或 list（多筆）
        if isinstance(result, dict):
            return [result]
        if isinstance(result, list):
            return result
        return None
    except Exception as e:
        log.warning(f"Request/parse failed for '{word}': {e}")
        return None


def extract_meaning(data: list) -> tuple[str | None, str | None, str | None]:
    """
    從 API 回傳的 DATA list 取出中文義和例句。

    實際欄位（2026-04-16 確認）：
      DATA.Explanation.chinese  → 中文詞義
      DATA.Name                 → 詞形（可忽略，已知）
    """
    meanings = []
    example_szy = None
    example_zh  = None

    for entry in data:
        # 中文義：Explanation.chinese（實際格式）
        expl = entry.get("Explanation")
        if isinstance(expl, dict):
            ch = expl.get("chinese") or expl.get("Chinese")
        elif isinstance(expl, str):
            ch = expl
        else:
            # fallback：舊格式欄位名稱
            ch = entry.get("CHWORD") or entry.get("chword")
        if ch:
            meanings.append(ch.strip())

    meaning_zh = "；".join(meanings) if meanings else None
    return meaning_zh, example_szy, example_zh


# ── 詞類推論（形態前綴/後綴） ────────────────────────────────────────────────────
_POS_PREFIXES: list[tuple[str, str]] = [
    ("maki", "v"), ("paki", "v"), ("pasi", "v"), ("pala", "v"),
    ("mala", "v"), ("paka", "v"), ("mika", "v"), ("saka", "v"),
    ("nisa", "v"), ("misa", "v"), ("mica", "v"), ("mipa", "v"),
    ("pipa", "v"), ("maci", "v"), ("paci", "v"), ("mita", "v"),
    ("miti", "v"), ("pita", "v"), ("miku", "v"), ("misu", "v"),
    ("mili", "v"), ("pili", "v"), ("misi", "v"),
    ("mi", "v"), ("ma", "v"), ("mu", "v"), ("pa", "v"),
    ("pi", "v"),
]

_POS_SUFFIXES: list[tuple[str, str]] = [
    ("an", "n"), ("ay", "n"), ("en", "v"),
]

def infer_pos(word: str) -> str | None:
    """根據撒奇萊雅語形態前綴/後綴推論詞類。僅作 fallback。"""
    w = word.lower().replace("'", "").replace("-", "")
    for prefix, pos in _POS_PREFIXES:
        if w.startswith(prefix) and len(w) > len(prefix) + 1:
            return pos
    for suffix, pos in _POS_SUFFIXES:
        if w.endswith(suffix) and len(w) > len(suffix) + 2:
            return pos
    return None


# ── DB 操作 ──────────────────────────────────────────────────────────────────
def get_pending_words(conn: sqlite3.Connection, overwrite_examples: bool = False) -> list[tuple[int, str]]:
    """
    回傳 (id, word) list。
    - 預設：★☆☆ 且 meaning_zh IS NULL（從未查過的詞）
    - overwrite_examples=True：額外包含 meaning_zh LIKE '[例]%'（有例句但無乾淨定義的詞）
    """
    cur = conn.cursor()
    if overwrite_examples:
        # 包含所有 [例] 例句前綴條目（confidence 可能是 ★★★，由 wiki 初始匯入設定），
        # 以及還沒查過的空白條目（confidence = ★☆☆）
        cur.execute("""
            SELECT id, word FROM lexicon
            WHERE (confidence = '★☆☆' AND meaning_zh IS NULL)
               OR meaning_zh LIKE '[例]%'
               OR meaning_zh LIKE '【例】%'
            ORDER BY id
        """)
    else:
        cur.execute("""
            SELECT id, word FROM lexicon
            WHERE confidence = '★☆☆' AND meaning_zh IS NULL
            ORDER BY id
        """)
    return cur.fetchall()


def update_word(conn: sqlite3.Connection, word_id: int,
                meaning_zh: str, example_szy: str | None,
                example_zh: str | None, dry_run: bool = False,
                pos: str | None = None):
    """更新 lexicon 的中文義、信心度、來源，以及例句（若原本為空）。
    pos 僅在欄位原本為 NULL 時才寫入（COALESCE 保護）。
    """
    if dry_run:
        log.info(f"  [dry-run] would UPDATE id={word_id} meaning_zh={meaning_zh!r} pos={pos!r}")
        return
    cur = conn.cursor()
    # 更新中文義 + 信心度 + 來源；若原本例句/pos 為空才補
    cur.execute("""
        UPDATE lexicon
        SET meaning_zh = ?,
            confidence = '★★★',
            source      = 'ilrdf_web',
            example_szy = COALESCE(example_szy, ?),
            example_zh  = COALESCE(example_zh,  ?),
            pos         = COALESCE(pos, ?)
        WHERE id = ?
    """, (meaning_zh, example_szy, example_zh, pos, word_id))
    conn.commit()


# ── 主流程 ───────────────────────────────────────────────────────────────────
def main(dry_run: bool = False, limit: int | None = None,
         overwrite_examples: bool = False, infer_pos_only: bool = False):
    if not DB.exists():
        print(f"找不到資料庫：{DB}")
        return

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # --infer-pos-only：只跑形態推論，不呼叫 API
    if infer_pos_only:
        rows = conn.execute("SELECT id, word FROM lexicon WHERE pos IS NULL").fetchall()
        updated = 0
        for wid, word in rows:
            p = infer_pos(word)
            if p:
                conn.execute("UPDATE lexicon SET pos=? WHERE id=?", (p, wid))
                updated += 1
        conn.commit()
        conn.close()
        log.info(f"infer-pos-only: updated {updated}/{len(rows)}")
        return

    pending = get_pending_words(conn, overwrite_examples=overwrite_examples)
    if limit:
        pending = pending[:limit]

    total    = len(pending)
    found    = 0
    not_found = 0
    errors   = 0

    log.info(f"開始批次查詢，共 {total} 詞，dry_run={dry_run}")
    start_time = datetime.now()

    for i, (word_id, word) in enumerate(pending, 1):
        # 進度報告（每 100 詞）
        if i % 100 == 0:
            elapsed = (datetime.now() - start_time).seconds
            log.info(f"進度 {i}/{total}（找到 {found}，未找到 {not_found}，錯誤 {errors}）"
                     f"  已用 {elapsed}s")

        data = query_ilrdf(word)

        if data is None:
            errors += 1
            log.debug(f"  [{i}/{total}] {word}: API 失敗")
        else:
            meaning_zh, example_szy, example_zh = extract_meaning(data)
            if meaning_zh:
                found += 1
                log.info(f"  [{i}/{total}] {word}: {meaning_zh}")
                update_word(conn, word_id, meaning_zh, example_szy, example_zh, dry_run,
                            pos=infer_pos(word))
            else:
                not_found += 1
                log.debug(f"  [{i}/{total}] {word}: 無結果")

        time.sleep(SLEEP_SEC)

    conn.close()

    log.info("=" * 60)
    log.info(f"完成。找到：{found}  未找到：{not_found}  錯誤：{errors}  共：{total}")
    log.info(f"log 已寫入：{LOG}")


# ── CLI ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ILRDF 批次查詢，補 lexicon 中文義")
    parser.add_argument("--dry-run", action="store_true", help="只印不寫入 DB")
    parser.add_argument("--limit",   type=int, default=None, help="只處理前 N 個詞")
    parser.add_argument("--overwrite-examples", action="store_true",
                        help="也重跑 meaning_zh 為 [例] 開頭的詞（覆蓋舊例句）")
    parser.add_argument("--infer-pos-only", action="store_true",
                        help="只跑 pos 形態推論（不呼叫 API），掃 pos IS NULL 的詞條")
    args = parser.parse_args()
    main(dry_run=args.dry_run, limit=args.limit,
         overwrite_examples=args.overwrite_examples,
         infer_pos_only=args.infer_pos_only)
