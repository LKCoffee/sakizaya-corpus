"""
app.py — 撒奇萊雅語翻譯機（Lite）Gradio 介面
"""

import os
import sys

# 確保同目錄的 translate.py 可被 import
sys.path.insert(0, os.path.dirname(__file__))

import gradio as gr
from translate import detect_lang, find_similar, lookup_words_in_text

# DB 路徑：環境變數 SZY_DB，預設 ../sakizaya.db
DB_PATH = os.environ.get(
    "SZY_DB",
    os.path.join(os.path.dirname(__file__), "..", "sakizaya.db"),
)


def query_handler(text: str):
    text = (text or "").strip()
    if not text:
        return "（請輸入文字）", "", ""

    # ── 1. 語言偵測 ──
    lang = detect_lang(text)
    lang_label = "中文" if lang == "zh" else "撒奇萊雅語"
    detection_out = f"偵測到：{lang_label}"

    # ── 2. 相似例句（top 5）──
    similar = find_similar(DB_PATH, text, lang, top_k=5)
    if similar and similar[0]["score"] > 0:
        lines = []
        for r in similar:
            lines.append(f"【{r['score']:.4f}】 撒奇萊雅：{r['szy']}  ↔  中文：{r['zh']}")
        similar_out = "\n".join(lines)
    else:
        similar_out = "（無相似例句）"

    # ── 3. 詞典查詢 ──
    hits = lookup_words_in_text(DB_PATH, text)
    if hits:
        dict_lines = []
        for h in hits:
            line = f"• {h['word']} → {h.get('meaning_zh', '')}"
            if h.get("example_szy"):
                line += f"\n  例：{h['example_szy']}"
            if h.get("example_zh"):
                line += f"  /{h['example_zh']}"
            dict_lines.append(line)
        dict_out = "\n".join(dict_lines)
    else:
        dict_out = "（輸入文字中未找到詞典收錄詞彙）"

    return detection_out, similar_out, dict_out


# ── Gradio UI ──
with gr.Blocks(title="撒奇萊雅語翻譯機（Lite）") as demo:
    gr.Markdown("# 撒奇萊雅語翻譯機（Lite）")
    gr.Markdown("輸入中文或撒奇萊雅語，查詢相似例句與詞典釋義。")

    with gr.Row():
        input_box = gr.Textbox(
            label="輸入中文或撒奇萊雅語",
            placeholder="可貼整篇文章或單詞…",
            lines=6,
        )

    query_btn = gr.Button("查詢", variant="primary")

    with gr.Column():
        out_detection = gr.Textbox(label="語言偵測", interactive=False)
        out_similar = gr.Textbox(label="相似例句（top 5）", lines=8, interactive=False)
        out_dict = gr.Textbox(label="詞典查詢", lines=6, interactive=False)

    query_btn.click(
        fn=query_handler,
        inputs=[input_box],
        outputs=[out_detection, out_similar, out_dict],
    )

if __name__ == "__main__":
    demo.launch()
