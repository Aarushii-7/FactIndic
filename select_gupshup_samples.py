from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data/gupshup"

# 1. Load original validation files
with open(DATA_DIR / "val.source", "r", encoding="utf-8") as f:
    sources = [line.strip() for line in f if line.strip()]

with open(DATA_DIR / "val.target", "r", encoding="utf-8") as f:
    summaries = [line.strip() for line in f if line.strip()]

assert len(sources) == len(summaries), "Source-summary counts do not match!"
assert len(sources) >= 200, "Not enough validation samples!"

# 2. Build DataFrame without trailing newlines
df = pd.DataFrame({
    "original_index": range(len(sources)),
    "split": ["validation"] * len(sources),
    "source_text": sources,
    "reference_summary": summaries
})

# 3. Deterministically sample 200 items (matching original random_state=42)
sampled_df = (
    df.sample(n=200, random_state=42)
      .sort_values("original_index")
      .reset_index(drop=True)
)

# 4. Assign sample IDs
sampled_df.insert(0, "sample_id", [f"GUP_{i:03d}" for i in range(1, 201)])

# 5. Save candidate dataset
output_path = DATA_DIR / "gupshup_200_validation_candidates.csv"
sampled_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"Successfully selected {len(sampled_df)} clean GupShup validation candidates.")
print(f"Saved to: {output_path}")
