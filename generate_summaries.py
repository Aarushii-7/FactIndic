"""
FactIndic - Phase 3: LLM Summarization Baseline (Condition A vs. Condition B)
Generates summaries using Gemini API under two controlled prompt conditions:
  Condition A: Standard concise prompt
  Condition B: Factuality-aware prompt
Supports batching, resume-from-checkpoint, and pilot runs (--limit).
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("\n[ERROR] 'google-genai' is not installed in your environment.")
    print("Please run: pip install google-genai python-dotenv\n")
    sys.exit(1)

# Prompt definitions matching Section 6 of FactIndic Project Guide
PROMPT_STANDARD = (
    "Summarize the following document concisely. Include the main information "
    "and preserve the overall meaning. Do not add information that is unrelated "
    "to the document.\n\n"
    "Document:\n{source_text}\n\n"
    "Summary:"
)

PROMPT_FACTUALITY = (
    "Summarize the document concisely using only information supported by the source. "
    "Preserve names, numbers, dates, places, events, and relationships accurately. "
    "Do not guess, infer unsupported causes, or add outside knowledge. "
    "Preserve the meaning of Indic-English code-mixed expressions. "
    "If a detail is unclear, omit it rather than inventing it.\n\n"
    "Document:\n{source_text}\n\n"
    "Summary:"
)

def build_client(api_key: str):
    if not api_key:
        print("\n[ERROR] Gemini API key not found!")
        print("Set it in a .env file: GEMINI_API_KEY=\"your_key_here\"")
        print("Or export it: export GEMINI_API_KEY=\"your_key_here\"\n")
        sys.exit(1)
    return genai.Client(api_key=api_key)

def generate_summary(client, model_name: str, prompt: str, temperature: float = 0.2, max_retries: int = 5):
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=350,
                ),
            )
            latency = time.time() - start_time
            text = response.text.strip() if response.text else ""
            return text, round(latency, 2)
        except Exception as e:
            err_str = str(e)
            if any(code in err_str for code in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"]):
                wait_time = (2 ** attempt) * 4  # 4s, 8s, 16s, 32s...
                print(f"      [Retry {attempt + 1}/{max_retries}] Server busy / high demand. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e
    raise RuntimeError(f"Failed after {max_retries} attempts due to server demand.")

def run_baseline(
    input_csv: Path,
    output_csv: Path,
    model_name: str = "gemini-3.8-flash",
    limit: int = None,
    delay_sec: float = 2.5,
):
    client = build_client(API_KEY)
    df = pd.read_csv(input_csv)

    print(f"\nLoaded {len(df)} candidate records from: {input_csv}")

    # Resume from existing checkpoint if present
    if output_csv.exists():
        existing_df = pd.read_csv(output_csv)
        # Only treat as completed if both summaries succeeded (not starting with ERROR:)
        valid_mask = (
            ~existing_df["summary_A_standard"].astype(str).str.startswith("ERROR:") &
            ~existing_df["summary_B_factuality"].astype(str).str.startswith("ERROR:")
        )
        valid_df = existing_df[valid_mask]
        completed_ids = set(valid_df["sample_id"].tolist())
        print(f"Found existing output with {len(completed_ids)} successfully completed records. Resuming...")
        results = valid_df.to_dict(orient="records")
    else:
        completed_ids = set()
        results = []

    # Filter remaining
    remaining = df[~df["sample_id"].isin(completed_ids)]

    if limit is not None:
        remaining = remaining.head(limit)
        print(f"Running on pilot slice of {len(remaining)} sample(s)...")
    else:
        print(f"Processing remaining {len(remaining)} sample(s)...")

    if len(remaining) == 0:
        print("All requested samples have already been processed!")
        return

    total = len(remaining)

    for i, (_, row) in enumerate(remaining.iterrows(), start=1):
        sample_id = row["sample_id"]
        source_text = str(row["source_text"]).strip()
        lang = row.get("language", "unknown")

        print(f"\n[{i}/{total}] Processing {sample_id} ({lang})...")

        # 1. Condition A: Standard prompt
        prompt_a = PROMPT_STANDARD.format(source_text=source_text)
        try:
            sum_a, lat_a = generate_summary(client, model_name, prompt_a)
            print(f"   ✓ Condition A generated in {lat_a}s")
        except Exception as e:
            print(f"   ✗ Error in Condition A: {e}")
            sum_a, lat_a = f"ERROR: {e}", 0.0

        time.sleep(delay_sec)

        # 2. Condition B: Factuality-aware prompt
        prompt_b = PROMPT_FACTUALITY.format(source_text=source_text)
        try:
            sum_b, lat_b = generate_summary(client, model_name, prompt_b)
            print(f"   ✓ Condition B generated in {lat_b}s")
        except Exception as e:
            print(f"   ✗ Error in Condition B: {e}")
            sum_b, lat_b = f"ERROR: {e}", 0.0

        record = {
            "sample_id": sample_id,
            "original_id": row.get("original_id", ""),
            "dataset": row.get("dataset", ""),
            "language": lang,
            "language_type": row.get("language_type", ""),
            "genre": row.get("genre", ""),
            "source_text": source_text,
            "reference_summary": str(row.get("reference_summary", "")).strip(),
            "summary_A_standard": sum_a,
            "summary_B_factuality": sum_b,
            "latency_A_sec": lat_a,
            "latency_B_sec": lat_b,
            "model_name": model_name,
            "created_at": datetime.now().isoformat(),
        }

        results.append(record)

        # Checkpoint to CSV after each record
        checkpoint_df = pd.DataFrame(results)
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_df.to_csv(output_csv, index=False, encoding="utf-8-sig")

        time.sleep(delay_sec)

    print(f"\nCompleted! Results saved to: {output_csv}")

def main():
    parser = argparse.ArgumentParser(description="FactIndic Phase 3: LLM Summarization Baseline")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/candidates_master.csv"),
        help="Path to candidates_master.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/summaries_baseline_A_B.csv"),
        help="Path to save generated summaries",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-3.8-flash",
        help="Gemini model name (default: gemini-3.8-flash)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Run pilot on first N records (e.g. --limit 5)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.5,
        help="Seconds delay between API calls to stay within rate limits",
    )

    args = parser.parse_args()
    run_baseline(
        input_csv=args.input,
        output_csv=args.output,
        model_name=args.model,
        limit=args.limit,
        delay_sec=args.delay,
    )

if __name__ == "__main__":
    main()
