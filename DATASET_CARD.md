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

The Sakizaya Language Corpus is a parallel text and lexicon dataset for the Sakizaya language (ISO 639-3: `szy`), an Austronesian language indigenous to the Hualien coastal plain of Taiwan. Sakizaya is a critically endangered language with an estimated few hundred fluent speakers remaining.

This dataset contains:
- **59,512 parallel sentence pairs** (Sakizaya ↔ Traditional Chinese)
- **6,173 lexicon entries** with part-of-speech, definitions, confidence scores, and usage examples

The corpus is intended to support NLP research, machine translation development, and language documentation efforts for low-resource indigenous languages.

## Languages

| Code | Language | Script | Notes |
|------|----------|--------|-------|
| `szy` | Sakizaya | Latin (romanized) | Austronesian; spoken in Hualien, Taiwan |
| `zh` | Traditional Chinese | Han (Traditional) | Used as pivot/target language |

## Data Sources

- **ILRDF (Indigenous Languages Research and Development Foundation, Taiwan)** — official Sakizaya language materials and educational texts
- **Wikipedia (Sakizaya-language articles)** — encyclopedic content scraped and aligned
- **Local documents** — supplementary texts from community and educational sources

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
