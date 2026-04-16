"""
fetch_alr.py — 朗聲四起競賽文章抓取
https://alr.alcd.center/article/picked

每年 3 組 × 4 篇 = 12 篇，9 年共 108 篇高品質平行語料
撒奇萊雅語 (col=2) 各年全抓

Usage:
    python fetch_alr.py
"""

import sqlite3
import time
import re
import logging
import sys
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DB_PATH = Path(r"C:\Users\User\sakizaya_corpus\sakizaya.db")
BASE_URL = "https://alr.alcd.center"
SZY_COL = 2   # 撒奇萊雅語語別代碼
YEARS = [105, 106, 107, 108, 110, 111, 112, 113, 114]  # 109 缺
GROUPS = [1, 2, 3]   # 1=高中, 2=國中, 3=國小
ARTICLES_PER_GROUP = 4
SOURCE_TAG = "alr_competition"
RATE_LIMIT = 0.5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            r"C:\Users\User\sakizaya_corpus\fetch_alr.log", encoding="utf-8"
        ),
    ],
)
log = logging.getLogger(__name__)


def cjk_ratio(text: str) -> float:
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return cjk / len(text) if text else 0.0


def latin_ratio(text: str) -> float:
    s = text.replace(" ", "")
    if not s:
        return 0.0
    lat = sum(1 for ch in s if unicodedata.category(ch).startswith("L"))
    return lat / len(s)


def classify(text: str) -> str:
    text = text.strip()
    if len(text) < 5:
        return "skip"
    if cjk_ratio(text) >= 0.35:
        return "zh"
    if cjk_ratio(text) < 0.05 and latin_ratio(text) >= 0.4:
        return "szy"
    return "skip"


def get_szy_article_ids(session: requests.Session, year: int) -> list[int]:
    """
    從 /article/picked?y={year} 抓撒奇萊雅語 article ID。
    頁面結構：每個 tr 含「撒奇萊雅語」 = 一篇文章，取第一個 article/view 連結。
    """
    url = f"{BASE_URL}/article/picked?y={year}"
    try:
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        log.warning("Year %d failed: %s", year, e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    seen: set[int] = set()
    ids: list[int] = []

    for tag in soup.find_all(string=re.compile("撒奇萊雅")):
        tr = tag.find_parent("tr")
        if not tr:
            continue
        a = tr.find("a", href=re.compile(r"/article/view/\d+"))
        if not a:
            continue
        m = re.search(r"/article/view/(\d+)", a["href"])
        if m:
            aid = int(m.group(1))
            if aid not in seen:
                seen.add(aid)
                ids.append(aid)

    return ids


def fetch_article(session: requests.Session, article_id: int) -> dict | None:
    """抓單篇文章，回傳 {szy: [...], zh: [...], title_szy, title_zh, year, group}"""
    url = f"{BASE_URL}/article/view/{article_id}"
    try:
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        log.warning("Article %d failed: %s", article_id, e)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # 抽所有段落文字
    # 直接從 p 標籤抓（不過濾 nav，因為 navbar class 含 nav 會誤殺所有內容）
    paras = []
    for p in soup.find_all("p"):
        text = re.sub(r"\s+", " ", p.get_text(" ", strip=True)).strip()
        if len(text) >= 5:
            paras.append(text)

    # 去重（保序）
    seen = set()
    unique_paras = []
    for p in paras:
        if p not in seen:
            seen.add(p)
            unique_paras.append(p)

    szy_paras = [p for p in unique_paras if classify(p) == "szy"]
    zh_paras  = [p for p in unique_paras if classify(p) == "zh"]

    if not szy_paras or not zh_paras:
        log.debug("Article %d: szy=%d zh=%d — skip", article_id, len(szy_paras), len(zh_paras))
        return None

    # 嘗試抓標題
    title_tag = soup.find("h1") or soup.find("h2")
    title_szy = ""
    title_zh = ""
    if title_tag:
        t = title_tag.get_text(" ", strip=True)
        if classify(t) == "szy":
            title_szy = t
        elif classify(t) == "zh":
            title_zh = t

    return {
        "id": article_id,
        "title_szy": title_szy,
        "title_zh": title_zh,
        "szy": szy_paras,
        "zh": zh_paras,
    }


def pair_paragraphs(szy: list[str], zh: list[str]) -> list[tuple[str, str]]:
    """
    段落配對：不截斷，改用比例合併。
    - 相等：1:1 zip
    - szy > zh：把 szy 相鄰段落合併至 len(zh)，再 zip
    - zh > szy：把 zh 相鄰段落合併至 len(szy)，再 zip
    """
    if not szy or not zh:
        return []
    if len(szy) == len(zh):
        return list(zip(szy, zh))

    def merge_to_n(paras: list[str], n: int) -> list[str]:
        if len(paras) <= n:
            return paras
        result = []
        chunk = len(paras) / n
        for i in range(n):
            start = int(i * chunk)
            end = int((i + 1) * chunk)
            result.append(" ".join(paras[start:end]))
        return result

    if len(szy) > len(zh):
        return list(zip(merge_to_n(szy, len(zh)), zh))
    else:
        return list(zip(szy, merge_to_n(zh, len(szy))))


def already_scraped(conn: sqlite3.Connection) -> set[int]:
    rows = conn.execute(
        "SELECT DISTINCT CAST(article_title AS INTEGER) FROM parallel WHERE source=?",
        (SOURCE_TAG,)
    ).fetchall()
    return {r[0] for r in rows}


def insert_pairs(conn: sqlite3.Connection, article_id: int, pairs: list[tuple[str, str]]) -> int:
    conn.executemany(
        "INSERT INTO parallel (article_title, szy, zh, source) VALUES (?,?,?,?)",
        [(str(article_id), s, z, SOURCE_TAG) for s, z in pairs],
    )
    conn.commit()
    return len(pairs)


def main():
    conn = sqlite3.connect(DB_PATH)
    done = already_scraped(conn)
    log.info("Already scraped: %d ALR articles", len(done))

    session = requests.Session()
    session.headers.update({
        "User-Agent": "SakizayaCorpus/1.0 (research; contact myosotis0430@gmail.com)"
    })

    total_pairs = 0
    total_articles = 0

    for year in YEARS:
        log.info("── Year %d ──────────────────────────────────────", year)
        article_refs = get_szy_article_ids(session, year)
        time.sleep(RATE_LIMIT)

        if not article_refs:
            log.warning("Year %d: no articles found", year)
            continue

        log.info("Year %d: found %d article IDs", year, len(article_refs))

        for aid in article_refs:
            if aid in done:
                log.debug("Article %d already done, skip", aid)
                continue

            result = fetch_article(session, aid)  # type: ignore[arg-type]
            time.sleep(RATE_LIMIT)

            if not result:
                log.info("  [%d] no parallel content", aid)
                # 插入 sentinel 避免重複抓
                conn.execute(
                    "INSERT OR IGNORE INTO parallel (article_title,szy,zh,source) VALUES(?,?,?,?)",
                    (str(aid), "", "", SOURCE_TAG + "_empty"),
                )
                conn.commit()
                continue

            pairs = pair_paragraphs(result["szy"], result["zh"])
            n = insert_pairs(conn, aid, pairs)
            total_pairs += n
            total_articles += 1
            log.info("  [%d] szy=%d zh=%d → %d pairs", aid, len(result["szy"]), len(result["zh"]), n)

    log.info("═══════════════════════════════════════")
    log.info("Done. Articles: %d | Pairs inserted: %d", total_articles, total_pairs)
    conn.close()


if __name__ == "__main__":
    main()
