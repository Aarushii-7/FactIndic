"""
FactIndic - Phase 3 (Local Execution): Open-Source LLM Summarization Baseline
Runs 100% locally on Apple Silicon GPU (MPS) using PyTorch & Hugging Face Transformers.
No API keys, no internet quota, no rate limits.
Default model: Qwen/Qwen2.5-1.5B-Instruct (lightweight, state-of-the-art Hindi/English/Hinglish support).
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import torch

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
except ImportError:
    print("\n[ERROR] 'transformers' is not installed.")
    print("Run: pip install transformers torch\n")
    sys.exit(1)

PROMPT_STANDARD = (
    "Summarize the following document concisely. Include the main information "
    "and preserve the overall meaning. Do not add information that is unrelated to the document.\n\n"
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

def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    return "cpu"

def load_local_pipeline(model_id: str):
    device_str = get_device()
    print(f"\n==================================================")
    print(f"Loading local model: {model_id}")
    print(f"Acceleration Device: {device_str.upper()} (Apple Silicon GPU)")
    print(f"==================================================")

    print("Downloading/loading tokenizer and weights (cached automatically)...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(model_id)

    dtype = torch.float16 if device_str in ["mps", "cuda"] else torch.float32
    try:
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype, local_files_only=True)
    except Exception:
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype)
    model.to(torch.device(device_str))
    model.eval()

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )
    print("Model loaded successfully and ready for inference!\n")
    return pipe

def generate_local_summary(pipe, prompt: str):
    start = time.time()
    messages = [
        {"role": "system", "content": "You are a concise, factual summarization assistant. Produce only the summary."},
        {"role": "user", "content": prompt}
    ]
    outputs = pipe(
        messages,
        max_new_tokens=250,
        temperature=0.2,
        do_sample=True,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    latency = time.time() - start
    generated = outputs[0]["generated_text"][-1]["content"].strip()
    return generated, round(latency, 2)

def run_local_baseline(
    input_csv: Path,
    output_csv: Path,
    model_id: str = "Qwen/Qwen2.5-1.5B-Instruct",
    limit: int = 5,
    balanced: int = None,
):
    pipe = load_local_pipeline(model_id)
    df = pd.read_csv(input_csv)

    print(f"Loaded {len(df)} candidate records from: {input_csv}")

    # Resume from existing checkpoint if present
    if output_csv.exists():
        existing_df = pd.read_csv(output_csv)
        completed_ids = set(existing_df["sample_id"].tolist())
        print(f"Found existing output with {len(completed_ids)} completed records. Resuming...")
        results = existing_df.to_dict(orient="records")
    else:
        completed_ids = set()
        results = []

    if balanced is not None and balanced > 0:
        dfs = []
        for lang in ["hindi", "english", "hinglish"]:
            lang_df = df[df["language"] == lang]
            lang_done = sum(1 for cid in completed_ids if cid in set(lang_df["sample_id"]))
            needed = max(0, balanced - lang_done)
            lang_rem = lang_df[~lang_df["sample_id"].isin(completed_ids)]
            dfs.append(lang_rem.head(needed))
        remaining = pd.concat(dfs, ignore_index=True)
        print(f"Selected balanced batch: {len(remaining)} sample(s) to reach target of {balanced} per language ({balanced*3} total)...")
    else:
        remaining = df[~df["sample_id"].isin(completed_ids)]
        if limit is not None and limit > 0:
            remaining = remaining.head(limit)

    total = len(remaining)
    if total == 0:
        print("All requested samples have already been processed!")
        return

    print(f"Generating summaries for {total} sample(s) on your Mac...\n")

    for i, (_, row) in enumerate(remaining.iterrows(), start=1):
        sample_id = row["sample_id"]
        source_text = str(row["source_text"]).strip()
        lang = row.get("language", "unknown")

        print(f"[{i}/{total}] Processing {sample_id} ({lang})...")

        # Condition A: Standard prompt
        prompt_a = PROMPT_STANDARD.format(source_text=source_text)
        sum_a, lat_a = generate_local_summary(pipe, prompt_a)
        print(f"   ✓ Condition A generated in {lat_a}s")

        # Condition B: Factuality-aware prompt
        prompt_b = PROMPT_FACTUALITY.format(source_text=source_text)
        sum_b, lat_b = generate_local_summary(pipe, prompt_b)
        print(f"   ✓ Condition B generated in {lat_b}s")

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
            "model_name": model_id,
            "created_at": datetime.now().isoformat(),
        }

        results.append(record)

        # Checkpoint after each sample
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(results).to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"\nCompleted! Results saved to: {output_csv}")

def main():
    parser = argparse.ArgumentParser(description="FactIndic Phase 3: Local LLM Summarization Baseline")
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
        default="Qwen/Qwen2.5-1.5B-Instruct",
        help="HuggingFace model ID (default: Qwen/Qwen2.5-1.5B-Instruct)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of records to process (e.g. --limit 10)",
    )
    parser.add_argument(
        "--balanced",
        type=int,
        default=None,
        help="Process N records per language (e.g. --balanced 5 gives 5 Hindi, 5 English, 5 Hinglish)",
    )

    args = parser.parse_args()
    run_local_baseline(args.input, args.output, args.model, args.limit, args.balanced)

if __name__ == "__main__":
    main()
