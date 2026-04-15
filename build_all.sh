#!/bin/bash
# Sakizaya Corpus Builder
# 從原始資料建立完整資料庫

set -e
echo "=== Sakizaya Corpus Builder ==="
echo ""

# 1. 建立基礎 DB（FormosanBank XML）
echo "[1/4] 解析 FormosanBank XML..."
python build_db.py

# 2. 抽取平行語料（離線 Wikipedia dump）
echo "[2/4] 抽取平行語料..."
python extract_parallel.py
python extract_parallel_v2.py

# 3. 匯入 ILRDF 辭典（離線 XML）
echo "[3/4] 匯入 ILRDF 辭典..."
python import_ilrdf_xml.py

# 4. 建立 lexicon
echo "[4/4] 建立詞典..."
python build_lexicon.py

echo ""
echo "=== 完成 ==="
python query.py stats
