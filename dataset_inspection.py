
import os
import re
import html
import pandas as pd
from datasets import load_dataset

# ==========================================
# 1. CREATE PROJECT FOLDERS
# ==========================================

os.makedirs("data/ilsum", exist_ok=True)

# ==========================================
# 2. DOWNLOAD ILSUM DATASETS
# ==========================================

print("\n========== DOWNLOADING DATASETS ==========")

print("\nLoading Hindi dataset...")
hindi_data = load_dataset("ILSUM/ILSUM-2.0", "Hindi")

print("\nLoading English dataset...")
english_data = load_dataset("ILSUM/ILSUM-2.0", "English")

# ==========================================
# 3. DISPLAY DATASET INFORMATION
# ==========================================

def show_dataset_info(dataset, language):

    print("\n==========", language, "DATASET ==========")

    for split in dataset.keys():

        print("\nSplit:", split)
        print("Number of records:", len(dataset[split]))
        print("Columns:", dataset[split].column_names)

    print("\nFirst training record:")
    print(dataset["train"][0])


show_dataset_info(hindi_data, "HINDI")
show_dataset_info(english_data, "ENGLISH")

# ==========================================
# 4. CONVERT TRAINING DATA INTO DATAFRAMES
# ==========================================

hindi_df = hindi_data["train"].to_pandas()
english_df = english_data["train"].to_pandas()

# ==========================================
# 5. INITIAL DATA QUALITY INSPECTION
# ==========================================

def inspect_data(df, language):

    print("\n==========", language, "DATA QUALITY ==========")

    print("Total records:", len(df))

    print("\nMissing values:")
    print(df[["Article", "Summary"]].isnull().sum())

    print("\nDuplicate articles:",
          df["Article"].dropna().duplicated().sum())

    print("\nAverage article length:",
          df["Article"].dropna().str.len().mean())

    print("Average summary length:",
          df["Summary"].dropna().str.len().mean())

    print("Shortest article:",
          df["Article"].dropna().str.len().min())

    print("Longest article:",
          df["Article"].dropna().str.len().max())


inspect_data(hindi_df, "HINDI")
inspect_data(english_df, "ENGLISH")

# ==========================================
# 6. INSPECT SHORT AND LONG ARTICLES
# ==========================================

def inspect_lengths(df, language):

    print("\n==========", language, "ARTICLE LENGTH CHECK ==========")

    article_lengths = df["Article"].fillna("").str.len()

    short_articles = df[article_lengths < 500]
    long_articles = df[article_lengths > 20000]

    print("Articles shorter than 500 characters:",
          len(short_articles))

    print("Articles longer than 20,000 characters:",
          len(long_articles))

    print("\nFirst 5 short articles:")

    for _, row in short_articles.head(5).iterrows():

        print("\nID:", row["id"])
        print("Article:", str(row["Article"])[:300])
        print("Summary:", str(row["Summary"])[:150])

    print("\nFirst 5 unusually long articles:")

    for _, row in long_articles.head(5).iterrows():

        print("\nID:", row["id"])
        print("Article length:", len(str(row["Article"])))
        print("Article preview:", str(row["Article"])[:300])


inspect_lengths(hindi_df, "HINDI")
inspect_lengths(english_df, "ENGLISH")

# ==========================================
# 7. CLEAN TEXT
# ==========================================

def clean_text(text):

    if pd.isna(text):
        return ""

    text = html.unescape(str(text))
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================
# 8. FILTER DATA
# ==========================================

def filter_data(df, language):

    df = df.copy()

    print("\n========== FILTERING", language, "==========")

    # Clean article and summary
    df["Article"] = df["Article"].apply(clean_text)
    df["Summary"] = df["Summary"].apply(clean_text)
    df["Heading"] = df["Heading"].apply(clean_text)

    original_count = len(df)

    # Remove empty articles and summaries
    df = df[
        (df["Article"] != "") &
        (df["Summary"] != "")
    ]

    after_empty = len(df)

    # Remove articles shorter than 500 characters
    df = df[df["Article"].str.len() >= 500]

    after_short = len(df)

    # Remove articles longer than 20,000 characters
    df = df[df["Article"].str.len() <= 20000]

    after_long = len(df)

    # Remove duplicate articles
    df = df.drop_duplicates(subset=["Article"])

    after_duplicates = len(df)

    print("Original records:", original_count)
    print("After removing empty records:", after_empty)
    print("After removing short articles:", after_short)
    print("After removing long articles:", after_long)
    print("After removing duplicates:", after_duplicates)

    print("Final filtered records:", len(df))

    return df


hindi_clean = filter_data(hindi_df, "HINDI")
english_clean = filter_data(english_df, "ENGLISH")

# ==========================================
# 9. DISPLAY FILTERED DATA SAMPLES
# ==========================================

def show_samples(df, language):

    print("\n==========", language, "FILTERED SAMPLES ==========")

    for _, row in df.head(5).iterrows():

        print("\nID:", row["id"])
        print("Heading:", row["Heading"])
        print("Article:", row["Article"][:400])
        print("Summary:", row["Summary"][:200])
        print("-" * 60)


show_samples(hindi_clean, "HINDI")
show_samples(english_clean, "ENGLISH")

# ==========================================
# 10. SAVE FILTERED DATASETS
# ==========================================

hindi_clean.to_csv(
    "data/ilsum/hindi_filtered.csv",
    index=False,
    encoding="utf-8-sig"
)

english_clean.to_csv(
    "data/ilsum/english_filtered.csv",
    index=False,
    encoding="utf-8-sig"
)

# ==========================================
# 11. SAVE INSPECTION REPORT
# ==========================================

report = pd.DataFrame([
    {
        "Language": "Hindi",
        "Original records": len(hindi_df),
        "Filtered records": len(hindi_clean),
        "Removed records": len(hindi_df) - len(hindi_clean)
    },
    {
        "Language": "English",
        "Original records": len(english_df),
        "Filtered records": len(english_clean),
        "Removed records": len(english_df) - len(english_clean)
    }
])

report.to_csv(
    "data/ilsum/inspection_report.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n========== FINAL RESULT ==========")
print(report.to_string(index=False))

print("\nFiltered datasets saved successfully!")
print("Location: data/ilsum/")
