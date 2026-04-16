"""
ollama_translate.py — Ollama LLM 翻譯層（AI 版）

呼叫本機 Ollama，以 RAG 例句作為 few-shot context，翻譯整段文字。
依賴：requests（標準函式庫外唯一依賴）
"""

import re
import requests
import json

# 模型偶爾無視 no-paren prompt，在 szy 輸出裡夾中文解釋如「kapi（咖啡）」。
# 短括號（≤8 字）一律剝除；保留長括號以防誤傷合法引用。
_PAREN_RE = re.compile(r"[（(][^）)]{1,8}[）)]")

OLLAMA_URL = "http://localhost:11434/api/generate"
# 預設用 qwen3.5:latest；可用環境變數 OLLAMA_MODEL 覆蓋（e.g., qwen2.5:1.5b）
import os as _os
MODEL = _os.environ.get("OLLAMA_MODEL", "qwen3.5:latest")


def is_ollama_running() -> bool:
    """檢查 Ollama 是否在跑（呼叫 /api/tags 端點）。"""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def build_prompt(text: str, lang: str, examples: list[dict]) -> str:
    """
    建立翻譯 prompt。

    格式：
      System: 你是撒奇萊雅語翻譯助手。以下是參考例句：
      [例句1: szy ↔ zh]
      [例句2: szy ↔ zh]
      ...
      請翻譯以下[中文/撒奇萊雅語]：[text]
      直接輸出翻譯結果，不要解釋。

    Parameters
    ----------
    text : str
        待翻譯文字。
    lang : str
        'zh'（中→撒奇萊雅）或 'szy'（撒奇萊雅→中）。
    examples : list[dict]
        來自 find_similar() 的例句列表，每筆含 'szy' 與 'zh' 欄位。

    Returns
    -------
    str
        完整 prompt 字串。
    """
    direction_label = "中文" if lang == "zh" else "撒奇萊雅語"
    target_label = "撒奇萊雅語" if lang == "zh" else "中文"

    if lang == "zh":
        lines = [
            "你是撒奇萊雅語（Sakizaya）翻譯專家。",
            "撒奇萊雅語是台灣原住民族語言，ISO 639-3 代碼：szy。",
            "你的任務：將中文翻譯為撒奇萊雅語。",
            "嚴格禁止：輸出英文、日文、韓文或其他語言。",
            "只允許：撒奇萊雅語輸出（拉丁字母拼寫）。",
            "若某個詞彙無法確定撒奇萊雅語對應，請直接跳過或使用最接近的詞，嚴禁在撒奇萊雅語輸出中夾入任何中文或英文（包括括號說明）。",
            "輸出格式（嚴格遵守，兩行，不多不少）：",
            "翻譯：<撒奇萊雅語譯文>",
            "信心：<高|中|低>",
            "信心判斷標準：高=有例句直接對應；中=部分詞彙有對應；低=多數詞彙無法確定。",
        ]
    else:
        lines = [
            "你是撒奇萊雅語（Sakizaya）翻譯專家。",
            "撒奇萊雅語是台灣原住民族語言，ISO 639-3 代碼：szy。",
            "你的任務：將撒奇萊雅語翻譯為中文。",
            "只允許：繁體中文輸出。",
            "輸出格式（嚴格遵守，兩行，不多不少）：",
            "翻譯：<中文譯文>",
            "信心：<高|中|低>",
            "信心判斷標準：高=詞義明確；中=部分確定；低=推測成分多。",
        ]

    if examples:
        lines.append("\n以下是參考例句（請依照這些例句的風格翻譯）：")
        for i, ex in enumerate(examples, 1):
            szy_text = ex.get("szy", "").strip()
            zh_text = ex.get("zh", "").strip()
            if szy_text and zh_text:
                lines.append(f"  例句{i}：撒奇萊雅語：{szy_text} ↔ 中文：{zh_text}")
        lines.append("")

    lines.append(f"請將以下{direction_label}翻譯為{target_label}，按上述格式輸出：")
    lines.append(text)

    return "\n".join(lines)


def _parse_output(raw: str) -> tuple[str, str]:
    """
    解析 model 輸出的兩行格式：
      翻譯：<text>
      信心：<高|中|低>
    回傳 (translation, confidence)。
    解析失敗時 confidence = '低'（保守處理）。
    """
    translation = ""
    confidence = "低"
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("翻譯："):
            translation = line[3:].strip()
        elif line.startswith("信心："):
            c = line[3:].strip()
            if c in ("高", "中", "低"):
                confidence = c
    # fallback：model 沒照格式輸出，把整行當翻譯，信心設低
    if not translation and raw.strip():
        translation = raw.strip()
        confidence = "低"
    return translation, confidence


def _deloop(text: str) -> str:
    """偵測並截斷重複短語（逗號分隔段落版本）。"""
    # 先嘗試按逗號分段找重複
    parts = [p.strip() for p in text.replace("，", ",").split(",")]
    if len(parts) > 3:
        seen = []
        for i, part in enumerate(parts):
            if part in seen[-4:]:           # 同樣片段出現在最近 4 段中
                return ", ".join(seen).rstrip(", 、，")
            seen.append(part)
    # fallback：連續重複字元序列（無分隔符）
    import re as _re
    m = _re.search(r"(.{6,}?)\1{2,}", text)
    if m:
        end = m.start() + len(m.group(1)) * 2
        return text[:end].rstrip(", 、，")
    return text


def translate_with_context(text: str, lang: str, examples: list[dict]) -> str:
    """
    用 examples 當 few-shot context，請 Ollama 翻譯 text。

    Parameters
    ----------
    text : str
        待翻譯的文字（可為多句）。
    lang : str
        'zh'（中文→撒奇萊雅）或 'szy'（撒奇萊雅→中文）。
    examples : list[dict]
        find_similar() 回傳的例句，每筆含 'szy' 與 'zh'。

    Returns
    -------
    str
        翻譯結果字串；失敗時回傳空字串。
    """
    if not text or not text.strip():
        return ""

    # szy→zh 無 RAG 防線：撒奇萊雅語→中文方向時，若 RAG 找不到任何有分數的例句，
    # 模型單靠英譯-再-中譯的路徑幻覺率太高 → 直接放棄輸出，讓 UI 顯示「語料不足」。
    if lang == "szy":
        top_score = max((ex.get("score", 0) for ex in examples), default=0)
        if top_score == 0:
            return ""

    prompt = build_prompt(text, lang, examples)

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 200,
            "repeat_penalty": 2.0,
            "repeat_last_n": 256,
            "stop": ["\n\n", "---", "注：", "備註：", "說明："],
        },
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        raw = data.get("response", "").strip()
        translation, confidence = _parse_output(_deloop(raw))
        translation = _PAREN_RE.sub("", translation).strip()
        if not translation:
            return ""
        if confidence == "低":
            return ""   # 信心低：不輸出，讓 UI 顯示「語料不足」
        conf_label = "★★★" if confidence == "高" else "★★☆"
        return f"{translation}　[{conf_label}]"
    except requests.exceptions.ConnectionError:
        print("[ollama_translate] 無法連線到 Ollama，請確認 Ollama 正在執行。")
        return ""
    except requests.exceptions.Timeout:
        print("[ollama_translate] Ollama 回應逾時（>60s），請檢查模型是否載入完畢。")
        return ""
    except requests.exceptions.HTTPError as e:
        print(f"[ollama_translate] HTTP 錯誤：{e}")
        return ""
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[ollama_translate] 解析回應失敗：{e}")
        return ""
    except Exception as e:
        print(f"[ollama_translate] 未預期錯誤：{e}")
        return ""


# ---------------------------------------------------------------------------
# 簡易 CLI 測試
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    print("=== ollama_translate 自測 ===")
    print(f"Ollama 運行中：{is_ollama_running()}")

    sample_examples = [
        {"szy": "Maray ko.", "zh": "我很好。"},
        {"szy": "Haw ko naw?", "zh": "你在哪裡？"},
        {"szy": "Mararum ko.", "zh": "我睡覺。"},
    ]

    test_text = "你好嗎？"
    print(f"\n測試輸入（zh→szy）：{test_text}")
    print("建立 prompt：")
    print(build_prompt(test_text, "zh", sample_examples))

    if is_ollama_running():
        result = translate_with_context(test_text, "zh", sample_examples)
        print(f"\n翻譯結果：{result}")
    else:
        print("\n[跳過實際翻譯，Ollama 未啟動]")

    sys.exit(0)
