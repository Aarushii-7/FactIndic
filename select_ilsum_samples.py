from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data/ilsum"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load filtered datasets
hindi = pd.read_csv(DATA_DIR / "hindi_filtered.csv")
english = pd.read_csv(DATA_DIR / "english_filtered.csv")

# Randomly select 150 records from each dataset (deterministic)
hindi_sample = hindi.sample(n=150, random_state=42)
english_sample = english.sample(n=150, random_state=42)

# Save selected records
hindi_sample.to_csv(
    DATA_DIR / "hindi_150_candidates.csv",
    index=False,
    encoding="utf-8-sig"
)

english_sample.to_csv(
    DATA_DIR / "english_150_candidates.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Hindi candidates:", len(hindi_sample))
print("English candidates:", len(english_sample))
print("Selection completed successfully!")
