"""
app_ai.py — 撒奇萊雅語翻譯機（AI 版）Gradio 介面

整合 translate.py（RAG 查詢層）+ ollama_translate.py（LLM 翻譯層），
提供完整的中文↔撒奇萊雅語 AI 翻譯體驗。

啟動方式：
    python app_ai.py
"""

import os
import gradio as gr

from translate import detect_lang, gather_rag_examples
from ollama_translate import is_ollama_running, translate_with_context

# DB 路徑：環境變數 SZY_DB，預設 ../sakizaya.db
DB_PATH = os.environ.get(
    "SZY_DB",
    os.path.join(os.path.dirname(__file__), "..", "sakizaya.db"),
)

# ---------------------------------------------------------------------------
# 翻譯核心邏輯
# ---------------------------------------------------------------------------

TOP_K_EXAMPLES = 3


def run_translation(text: str) -> tuple[str, str, str]:
    """
    主翻譯函式，供 Gradio 按鈕呼叫。

    Parameters
    ----------
    text : str
        使用者輸入的文字（可為多句或整篇文章）。

    Returns
    -------
    tuple[str, str, str]
        (ai_result, examples_md, ollama_status)
    """
    # 0. Ollama 狀態
    ollama_ok = is_ollama_running()
    ollama_status = "✅ 已連線" if ollama_ok else "❌ Ollama 未啟動，請先安裝並啟動 Ollama（https://ollama.ai）"

    if not text or not text.strip():
        return "", "", ollama_status

    if not ollama_ok:
        return (
            "（Ollama 未啟動，無法翻譯。請確認 Ollama 已安裝並在背景執行（系統匣有圖示），再重新整理頁面。）",
            "",
            ollama_status,
        )

    # 1. 偵測語言方向
    lang = detect_lang(text)

    # 2. RAG 例句
    top_examples = gather_rag_examples(DB_PATH, text, lang=lang, top_k=TOP_K_EXAMPLES, min_score=0.0)

    # 3. 呼叫 LLM 翻譯
    ai_result = translate_with_context(text, lang, top_examples)

    if not ai_result:
        ai_result = "（翻譯失敗，請確認 Ollama 模型已載入，或稍後再試。）"

    # 4. 組成參考例句 Markdown
    examples_md = _format_examples_md(top_examples, lang)

    return ai_result, examples_md, ollama_status


def _format_examples_md(examples: list[dict], lang: str) -> str:
    """將 RAG 例句轉為可讀的 Markdown 字串。"""
    if not examples:
        return "（無相關例句）"

    direction = "中文 → 撒奇萊雅語" if lang == "zh" else "撒奇萊雅語 → 中文"
    lines = [f"**語料方向：{direction}**\n"]

    for i, ex in enumerate(examples, 1):
        szy = ex.get("szy", "").strip()
        zh = ex.get("zh", "").strip()
        score = ex.get("score", None)
        score_str = f"（相似度 {score:.3f}）" if score is not None else ""
        lines.append(f"**例句 {i}** {score_str}")
        lines.append(f"- 撒奇萊雅語：`{szy}`")
        lines.append(f"- 中文：{zh}")
        lines.append("")

    return "\n".join(lines)


def refresh_ollama_status() -> str:
    """重新檢查 Ollama 狀態（供 Refresh 按鈕使用）。"""
    return "✅ 已連線" if is_ollama_running() else "❌ Ollama 未啟動，請先安裝並啟動 Ollama（https://ollama.ai）"


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

def build_ui() -> gr.Blocks:
    initial_status = refresh_ollama_status()

    with gr.Blocks(
        title="撒奇萊雅語翻譯機（AI 版）",
    ) as demo:

        gr.Markdown(
            """
            # 撒奇萊雅語翻譯機（AI 版）
            中文 ↔ 撒奇萊雅語｜Ollama LLM + 語料庫 RAG 加持
            """,
            elem_id="title",
        )

        with gr.Row():
            with gr.Column(scale=3):
                input_box = gr.Textbox(
                    label="輸入文字（可貼整篇文章）",
                    placeholder="在此輸入中文或撒奇萊雅語文字……",
                    lines=8,
                    max_lines=20,
                    elem_id="input-box",
                )
                translate_btn = gr.Button("翻譯", variant="primary", size="lg")

            with gr.Column(scale=3):
                output_box = gr.Textbox(
                    label="AI 翻譯結果",
                    lines=8,
                    max_lines=20,
                    interactive=False,
                    elem_id="output-box",
                )

        with gr.Accordion("參考例句（RAG 來源）", open=False):
            examples_box = gr.Markdown(
                value="（翻譯後會顯示前 3 筆最相關例句）",
                elem_classes=["examples-box"],
            )

        with gr.Row():
            ollama_status_box = gr.Textbox(
                label="Ollama 狀態",
                value=initial_status,
                interactive=False,
                scale=4,
            )
            refresh_btn = gr.Button("重新檢查", scale=1)

        # 事件綁定
        translate_btn.click(
            fn=run_translation,
            inputs=[input_box],
            outputs=[output_box, examples_box, ollama_status_box],
        )

        input_box.submit(
            fn=run_translation,
            inputs=[input_box],
            outputs=[output_box, examples_box, ollama_status_box],
        )

        refresh_btn.click(
            fn=refresh_ollama_status,
            inputs=[],
            outputs=[ollama_status_box],
        )

        gr.Markdown(
            """
            ---
            **提示**：語言方向自動偵測。輸入中文→翻成撒奇萊雅語；輸入撒奇萊雅語→翻成中文。
            翻譯品質受語料庫覆蓋率影響，生僻詞彙或罕見句型可能翻錯，請參閱 README_AI.md。
            """,
        )

    return demo


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        inbrowser=True,
        theme=gr.themes.Soft(),
        css=".examples-box { font-size: 0.9em; }",
    )
