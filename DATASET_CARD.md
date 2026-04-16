---
language:
- szy
- zh
license: cc-by-nc-sa-4.0
task_categories:
- translation
- text-generation
pretty_name: Sakizaya Language Corpus
size_categories:
- 10K<n<100K
---

# Sakizaya Language Corpus

## Dataset Description

The Sakizaya Language Corpus is a parallel text, lexicon, and monolingual dataset for the Sakizaya language (ISO 639-3: `szy`), an Austronesian language indigenous to the Hualien coastal plain of Taiwan. Sakizaya is a critically endangered language with an estimated few hundred fluent speakers remaining.

This dataset contains:
- **90,471 parallel sentence pairs** (Sakizaya ↔ Traditional Chinese) — in `parallel.csv`
- **6,173 lexicon entries** with part-of-speech, definitions, confidence scores, and usage examples — in `lexicon.csv`
- **5,363 Sakizaya Wikipedia articles** with sentence-level segmentation — in `sakizaya.db` tables `articles` + `sentences` (source_type `formosanbank_wiki`, sourced from FormosanBank's Sakizaya Wikipedia XML corpus)

The corpus is intended to support NLP research, machine translation development, and language documentation efforts for low-resource indigenous languages.

## Languages

| Code | Language | Script | Notes |
|------|----------|--------|-------|
| `szy` | Sakizaya | Latin (romanized) | Austronesian; spoken in Hualien, Taiwan |
| `zh` | Traditional Chinese | Han (Traditional) | Used as pivot/target language |

## Data Sources

- **FormosanBank** (joint project by NTU Linguistics, Boston College, MGH Institute of Health Professions) — Sakizaya Wikipedia XML corpus (5,363 articles with orthography QC). License: CC BY-SA 4.0. https://github.com/FormosanBank/FormosanBank
- **szy.Wikipedia (Wikimedia Foundation)** — Sakizaya-language encyclopedic articles (also accessed directly via Wikipedia dump and web scraping for parallel text extraction). License: CC BY-SA 4.0.
- **ILRDF (Indigenous Languages Research and Development Foundation, Taiwan / 原住民族語言研究發展基金會)** — Sakizaya e-dictionary (lexicon entries with examples). License: CC BY-NC 4.0. https://e-dictionary.ilrdf.org.tw
- **ALR "朗聲四起" (Aboriginal Language Revitalization Platform)** — 215 parallel pairs from Sakizaya-language articles authored for the National Language Competition. Maintained by NCCU Center for Aboriginal Studies (政大原民中心) under Taiwan MOE. https://alr.alcd.center
- **Local documents & community informants** — supplementary texts contributed by Sakizaya speakers and community sources

## Dataset Structure

### `parallel.csv`

Sentence-level parallel corpus aligned between Sakizaya and Traditional Chinese.

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Unique row identifier |
| `article_title` | string | Source article or document title |
| `szy` | string | Sakizaya text (romanized, length > 10 chars) |
| `zh` | string | Traditional Chinese translation (length > 3 chars) |
| `source` | string | Data source identifier (e.g., `ilrdf`, `wiki`) |

### `lexicon.csv`

Word-level lexicon with grammatical and semantic annotations.

| Column | Type | Description |
|--------|------|-------------|
| `word` | string | Sakizaya word form (romanized) |
| `pos` | string | Part of speech (e.g., `n`, `v`, `adj`) |
| `meaning_zh` | string | Meaning in Traditional Chinese |
| `confidence` | float | Confidence score of the entry (0.0–1.0) |
| `source` | string | Data source identifier |
| `example_szy` | string | Example sentence in Sakizaya (may be null) |
| `example_zh` | string | Example sentence in Traditional Chinese (may be null) |

### `articles` (in `sakizaya.db`)

Article-level metadata for Sakizaya Wikipedia pages processed from FormosanBank XML corpus.

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Unique article identifier |
| `title` | string | Article title |
| `source_url` | string | Original Wikipedia URL (from FormosanBank citation field) |
| `copyright` | string | Copyright notice (typically `CC BY-SA`) |
| `source_type` | string | Source identifier: `formosanbank_wiki` (FormosanBank Sakizaya Wikipedia XML) or `local_txt` (local supplementary texts) |

### `sentences` (in `sakizaya.db`)

Sentence-level monolingual Sakizaya text, tied to `articles` via `article_id`.

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Unique sentence identifier |
| `article_id` | integer | Foreign key to `articles.id` |
| `sent_idx` | integer | Sentence index within source article |
| `text` | string | Sakizaya sentence text (standard orthography preferred, falls back to original form if standard unavailable) |

## Usage Example

```python
import pandas as pd

# Load parallel corpus
parallel = pd.read_csv("parallel.csv", encoding="utf-8-sig")
print(f"Parallel pairs: {len(parallel):,}")
print(parallel.head())

# Load lexicon
lexicon = pd.read_csv("lexicon.csv", encoding="utf-8-sig")
print(f"Lexicon entries: {len(lexicon):,}")
print(lexicon[lexicon["pos"] == "n"].head())

# Filter by source
ilrdf_pairs = parallel[parallel["source"] == "ilrdf"]
print(f"ILRDF sentences: {len(ilrdf_pairs):,}")
```

## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{sakizaya_corpus_2026,
  title     = {Sakizaya Language Corpus: Parallel Text and Lexicon},
  year      = {2026},
  language  = {szy, zh},
  license   = {CC BY-NC-SA 4.0},
  note      = {Sakizaya--Traditional Chinese parallel corpus for NLP and language documentation}
}
```

## License

This dataset is released under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/) license.

- **Attribution** — You must give appropriate credit and indicate if changes were made.
- **NonCommercial** — You may not use the material for commercial purposes.
- **ShareAlike** — If you remix or build upon the material, you must distribute your contributions under the same license.

Source materials from ILRDF are used in accordance with their open educational licensing terms.
