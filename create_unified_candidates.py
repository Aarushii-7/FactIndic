from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

hi_path = BASE_DIR / "data/ilsum/hindi_150_candidates.csv"
en_path = BASE_DIR / "data/ilsum/english_150_candidates.csv"
gup_path = BASE_DIR / "data/gupshup/gupshup_200_validation_candidates.csv"

hi_df = pd.read_csv(hi_path)
en_df = pd.read_csv(en_path)
gup_df = pd.read_csv(gup_path)

records = []

# 1. Hindi ILSUM (150 candidates)
for idx, row in hi_df.iterrows():
    records.append({
        "sample_id": f"ILSUM_HI_{idx+1:03d}",
        "original_id": str(row["id"]),
        "dataset": "ILSUM",
        "language": "hindi",
        "language_type": "monolingual_indic",
        "genre": "news",
        "heading": str(row["Heading"]).strip(),
        "source_text": str(row["Article"]).strip(),
        "reference_summary": str(row["Summary"]).strip()
    })

# 2. English ILSUM (150 candidates)
for idx, row in en_df.iterrows():
    records.append({
        "sample_id": f"ILSUM_EN_{idx+1:03d}",
        "original_id": str(row["id"]),
        "dataset": "ILSUM",
        "language": "english",
        "language_type": "monolingual_english",
        "genre": "news",
        "heading": str(row["Heading"]).strip(),
        "source_text": str(row["Article"]).strip(),
        "reference_summary": str(row["Summary"]).strip()
    })

# 3. GupShup Hinglish (200 candidates)
for idx, row in gup_df.iterrows():
    records.append({
        "sample_id": str(row["sample_id"]),
        "original_id": str(row["original_index"]),
        "dataset": "GupShup",
        "language": "hinglish",
        "language_type": "code_mixed",
        "genre": "dialogue",
        "heading": "",
        "source_text": str(row["source_text"]).strip(),
        "reference_summary": str(row["reference_summary"]).strip()
    })

unified_df = pd.DataFrame(records)
output_master = BASE_DIR / "data/candidates_master.csv"
unified_df.to_csv(output_master, index=False, encoding="utf-8-sig")

print(f"Unified dataset created successfully with {len(unified_df)} rows!")
print("Breakdown by language:")
print(unified_df["language"].value_counts())
print(f"Saved to: {output_master}")
