"""
ollama_translate.py — Ollama LLM 翻譯層（AI 版）

呼叫本機 Ollama，以 RAG 例句作為 few-shot context，翻譯整段文字。
依賴：requests（標準函式庫外唯一依賴）
"""

import requests
import json

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
            "若某個詞彙無法確定撒奇萊雅語對應，可保留該詞原文並加括號。",
        ]
    else:
        lines = [
            "你是撒奇萊雅語（Sakizaya）翻譯專家。",
            "撒奇萊雅語是台灣原住民族語言，ISO 639-3 代碼：szy。",
            "你的任務：將撒奇萊雅語翻譯為中文。",
            "只允許：繁體中文輸出。",
        ]

    if examples:
        lines.append("\n以下是參考例句（請依照這些例句的風格翻譯）：")
        for i, ex in enumerate(examples, 1):
            szy_text = ex.get("szy", "").strip()
            zh_text = ex.get("zh", "").strip()
            if szy_text and zh_text:
                lines.append(f"  例句{i}：撒奇萊雅語：{szy_text} ↔ 中文：{zh_text}")
        lines.append("")

    lines.append(f"請將以下{direction_label}翻譯為{target_label}，直接輸出結果，不要解釋：")
    lines.append(text)

    return "\n".join(lines)


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

    prompt = build_prompt(text, lang, examples)

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 512,
            "repeat_penalty": 1.3,
            "repeat_last_n": 64,
        },
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        result = data.get("response", "").strip()
        return result
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
