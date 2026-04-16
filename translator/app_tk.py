"""
app_tk.py — 撒奇萊雅語翻譯機（獨立版，無需安裝任何套件）
用 tkinter 製作，可用 PyInstaller 打包成 .exe
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, font
from pathlib import Path

# ── DB 路徑 ─────────────────────────────────────────────────────
# PyInstaller 打包後，資料在 sys._MEIPASS 或 exe 同目錄
if getattr(sys, "frozen", False):
    # 打包後：exe 同目錄
    BASE = Path(sys.executable).parent
else:
    # 開發時：translator/ 的上一層（repo_root）
    BASE = Path(__file__).parent.parent

DB_PATH = str(os.environ.get("SZY_DB", BASE / "sakizaya.db"))

# ── 匯入核心引擎 ────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
try:
    from translate import detect_lang, find_similar, lookup_word, lookup_words_in_text, lookup_by_meaning, gather_rag_examples, classify_query_type
except ImportError:
    # 若找不到 translate.py，顯示錯誤
    import tkinter.messagebox as mb
    root = tk.Tk()
    root.withdraw()
    mb.showerror("錯誤", "找不到 translate.py，請確認檔案完整")
    sys.exit(1)


# ── UI ──────────────────────────────────────────────────────────

class SakizayaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("撒奇萊雅語翻譯工具")
        self.geometry("800x600")
        self.minsize(600, 450)
        self.configure(bg="#F5F0E8")
        self._build_ui()
        self._check_db()

    def _build_ui(self):
        BG = "#F5F0E8"
        ACCENT = "#7B6B52"
        BTN = "#5C7A4E"

        # ── 標題 ───────────────────────────────
        title_frame = tk.Frame(self, bg=ACCENT, pady=8)
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="撒奇萊雅語翻譯工具",
                 font=("微軟正黑體", 16, "bold"),
                 fg="white", bg=ACCENT).pack()
        tk.Label(title_frame, text="Sakizaya Language Tool · ISO 639-3: szy",
                 font=("微軟正黑體", 9),
                 fg="#D4C9B0", bg=ACCENT).pack()

        # ── 輸入區 ─────────────────────────────
        input_frame = tk.Frame(self, bg=BG, padx=15, pady=10)
        input_frame.pack(fill="x")

        # 方向選擇
        dir_frame = tk.Frame(input_frame, bg=BG)
        dir_frame.pack(anchor="w")
        tk.Label(dir_frame, text="翻譯方向：", bg=BG, fg=ACCENT,
                 font=("微軟正黑體", 10)).pack(side="left")
        self.direction = tk.StringVar(value="auto")
        for val, label in [("auto", "自動判斷"), ("zh2szy", "中文 → 撒奇萊雅語"), ("szy2zh", "撒奇萊雅語 → 中文")]:
            tk.Radiobutton(dir_frame, text=label, variable=self.direction,
                           value=val, bg=BG, fg="#333", activebackground=BG,
                           font=("微軟正黑體", 10)).pack(side="left", padx=5)

        # 輸入框
        tk.Label(input_frame, text="輸入文字：", bg=BG, fg=ACCENT,
                 font=("微軟正黑體", 10)).pack(anchor="w", pady=(8, 2))
        self.input_box = tk.Text(input_frame, height=3, font=("微軟正黑體", 12),
                                  relief="solid", bd=1, wrap="word")
        self.input_box.pack(fill="x")
        self.input_box.bind("<Return>", lambda e: self._on_query() or "break")

        # 查詢按鈕
        btn_frame = tk.Frame(input_frame, bg=BG)
        btn_frame.pack(anchor="e", pady=5)
        tk.Button(btn_frame, text="  查詢  ", command=self._on_query,
                  bg=BTN, fg="white", font=("微軟正黑體", 11, "bold"),
                  relief="flat", padx=10, pady=4,
                  activebackground="#4A6840").pack(side="right")
        tk.Button(btn_frame, text="清除", command=self._clear,
                  bg="#AAA", fg="white", font=("微軟正黑體", 10),
                  relief="flat", padx=8, pady=4).pack(side="right", padx=5)

        # ── 結果區 ─────────────────────────────
        result_frame = tk.Frame(self, bg=BG, padx=15)
        result_frame.pack(fill="both", expand=True, pady=(0, 10))

        # 分頁
        nb = ttk.Notebook(result_frame)
        nb.pack(fill="both", expand=True)

        self.tab_dict = self._make_tab(nb, "📖 詞典結果")
        self.tab_ex = self._make_tab(nb, "💬 相似例句")

        # 狀態列
        self.status_var = tk.StringVar(value="就緒")
        tk.Label(self, textvariable=self.status_var, bg=ACCENT, fg="white",
                 font=("微軟正黑體", 9), anchor="w", padx=10).pack(fill="x", side="bottom")

    def _make_tab(self, nb, title):
        frame = ttk.Frame(nb)
        nb.add(frame, text=title)
        box = scrolledtext.ScrolledText(frame, font=("微軟正黑體", 11),
                                         wrap="word", relief="flat", bd=0,
                                         bg="#FFFDF8", state="disabled")
        box.pack(fill="both", expand=True, padx=2, pady=2)
        return box

    def _set_text(self, box, text):
        box.config(state="normal")
        box.delete("1.0", "end")
        box.insert("end", text)
        box.config(state="disabled")

    def _on_query(self):
        text = self.input_box.get("1.0", "end").strip()
        if not text:
            return
        self.status_var.set("查詢中...")
        self.update_idletasks()

        direction = self.direction.get()
        if direction == "auto":
            lang = detect_lang(text)
        elif direction == "zh2szy":
            lang = "zh"
        else:
            lang = "szy"

        lang_label = "中文" if lang == "zh" else "撒奇萊雅語"

        # 詞典結果
        dict_lines = [f"偵測語言：{lang_label}\n"]
        entry = lookup_word(DB_PATH, text.strip())
        if entry:
            dict_lines.append(f"【{entry.get('word','—')}】")
            if entry.get('meaning_zh'):
                dict_lines.append(f"  中文：{entry['meaning_zh']}")
            if entry.get('example_szy'):
                dict_lines.append(f"  撒奇萊雅例句：{entry['example_szy']}")
            if entry.get('example_zh'):
                dict_lines.append(f"  例句中文：{entry['example_zh']}")
        else:
            hits = lookup_by_meaning(DB_PATH, text) if lang == "zh" else lookup_words_in_text(DB_PATH, text)
            if hits:
                dict_lines.append(f"找到 {len(hits)} 個詞：\n")
                for h in hits:
                    m = h.get('meaning_zh') or h.get('example_zh', '')
                    if m:
                        m = m[:60]
                    dict_lines.append(f"  {h['word']:<20} {m or '（詞典無中文義）'}")
            else:
                qtype = classify_query_type(text)
                if qtype == "modern":
                    dict_lines.append("（現代詞彙，撒奇萊雅語語料暫無收錄）")
                elif qtype == "abstract":
                    dict_lines.append("（抽象概念，現有語料可能無直接對應詞）")
                else:
                    dict_lines.append("（詞典無收錄，可嘗試查詢相近詞彙）")
        self._set_text(self.tab_dict, "\n".join(dict_lines))

        # 相似例句
        similar = gather_rag_examples(DB_PATH, text, lang, top_k=5)
        ex_lines = []
        if similar and similar[0]["score"] > 0:
            for r in similar:
                if r["score"] < 0.05:
                    break
                ex_lines.append(f"[相似度 {r['score']:.2f}]")
                ex_lines.append(f"  撒奇萊雅：{r['szy']}")
                ex_lines.append(f"  中文：    {r['zh']}")
                ex_lines.append("")
        else:
            ex_lines.append("（無相似例句）")
        self._set_text(self.tab_ex, "\n".join(ex_lines))

        self.status_var.set(f"完成 · DB: {DB_PATH}")

    def _clear(self):
        self.input_box.delete("1.0", "end")
        self._set_text(self.tab_dict, "")
        self._set_text(self.tab_ex, "")
        self.status_var.set("就緒")

    def _check_db(self):
        if not Path(DB_PATH).exists():
            import tkinter.messagebox as mb
            mb.showerror("找不到資料庫",
                         f"找不到 sakizaya.db\n\n預期位置：\n{DB_PATH}\n\n"
                         "請將 sakizaya.db 放到程式同一個資料夾。")


if __name__ == "__main__":
    app = SakizayaApp()
    app.mainloop()
