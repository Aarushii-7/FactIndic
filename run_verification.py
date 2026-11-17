"""
FactIndic - Phase 4: Full Verification Pipeline Runner
Loads generated summaries from Condition A and Condition B,
extracts atomic claims, retrieves top-k source evidence sentences,
and predicts factual consistency using Multilingual NLI.
Saves detailed claim audits and condition scorecard reports.
"""

import argparse
import time
from pathlib import Path
import pandas as pd
from datetime import datetime

from src.evidence_retriever import EvidenceRetriever
from src.claim_extractor import ClaimExtractor
from src.nli_verifier import NLIVerifier

def verify_single_summary(
    summary_text: str,
    source_text: str,
    genre: str,
    extractor: ClaimExtractor,
    retriever: EvidenceRetriever,
    verifier: NLIVerifier,
    top_k: int = 3,
):
    """Verifies all claims in a single summary against source_text."""
    claims = extractor.extract_claims(summary_text)
    claim_records = []

    for c in claims:
        claim_id = c["claim_id"]
        claim_text = c["claim_text"]

        # Retrieve top-k evidence sentences
        retrieved_units = retriever.retrieve(claim_text, source_text, genre=genre, top_k=top_k)
        evidence_text = " ".join([r["sentence"] for r in retrieved_units])
        avg_retrieval_score = (
            round(sum([r["score"] for r in retrieved_units]) / len(retrieved_units), 4)
            if retrieved_units else 0.0
        )

        # NLI verification
        nli_res = verifier.verify(premise=evidence_text, hypothesis=claim_text)

        claim_records.append({
            "claim_id": claim_id,
            "claim_text": claim_text,
            "retrieved_evidence": evidence_text,
            "retrieval_similarity": avg_retrieval_score,
            "nli_label": nli_res["label"],
            "confidence": nli_res["confidence"],
            "prob_entailment": nli_res["probabilities"].get("entailment", 0.0),
            "prob_contradiction": nli_res["probabilities"].get("contradiction", 0.0),
            "prob_neutral": nli_res["probabilities"].get("neutral", 0.0),
        })

    # Summary-level stats
    total_claims = len(claim_records)
    if total_claims > 0:
        entailments = sum(1 for c in claim_records if c["nli_label"] == "entailment")
        contradictions = sum(1 for c in claim_records if c["nli_label"] == "contradiction")
        neutrals = sum(1 for c in claim_records if c["nli_label"] == "neutral")

        support_rate = round((entailments / total_claims) * 100, 2)
        contradiction_rate = round((contradictions / total_claims) * 100, 2)
        neutral_rate = round((neutrals / total_claims) * 100, 2)
    else:
        entailments = contradictions = neutrals = 0
        support_rate = contradiction_rate = neutral_rate = 0.0

    stats = {
        "num_claims": total_claims,
        "entailments": entailments,
        "contradictions": contradictions,
        "neutrals": neutrals,
        "support_rate_pct": support_rate,
        "contradiction_rate_pct": contradiction_rate,
        "neutral_rate_pct": neutral_rate,
    }

    return claim_records, stats

def run_verification_pipeline(
    input_csv: Path,
    output_detailed: Path,
    output_summary: Path,
    limit: int = None,
    top_k: int = 3,
):
    print("\n" + "=" * 60)
    print("FACTINDIC - PHASE 4: VERIFICATION PIPELINE")
    print("=" * 60)

    # 1. Initialize components
    extractor = ClaimExtractor(pipe=None)  # rule-based sentence claims for fast, deterministic split
    retriever = EvidenceRetriever(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    verifier = NLIVerifier(
        model_name="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
    )

    df = pd.read_csv(input_csv)
    if limit is not None and limit > 0:
        df = df.head(limit)

    total_records = len(df)
    print(f"\nVerifying {total_records} baseline summaries (Conditions A & B)...")

    detailed_rows = []
    summary_rows = []

    for idx, row in df.iterrows():
        sample_id = row["sample_id"]
        lang = row.get("language", "unknown")
        genre = row.get("genre", "news")
        source_text = str(row["source_text"])

        sum_a = str(row.get("summary_A_standard", ""))
        sum_b = str(row.get("summary_B_factuality", ""))

        print(f"\n[{idx + 1}/{total_records}] Auditing {sample_id} ({lang}, {genre})...")

        # Verify Condition A
        claims_a, stats_a = verify_single_summary(
            summary_text=sum_a,
            source_text=source_text,
            genre=genre,
            extractor=extractor,
            retriever=retriever,
            verifier=verifier,
            top_k=top_k,
        )
        for c in claims_a:
            c.update({
                "sample_id": sample_id,
                "language": lang,
                "condition": "Condition_A_Standard",
            })
            detailed_rows.append(c)

        print(f"   Condition A: {stats_a['num_claims']} claims -> {stats_a['support_rate_pct']}% Support, {stats_a['contradiction_rate_pct']}% Contradiction")

        # Verify Condition B
        claims_b, stats_b = verify_single_summary(
            summary_text=sum_b,
            source_text=source_text,
            genre=genre,
            extractor=extractor,
            retriever=retriever,
            verifier=verifier,
            top_k=top_k,
        )
        for c in claims_b:
            c.update({
                "sample_id": sample_id,
                "language": lang,
                "condition": "Condition_B_Factuality",
            })
            detailed_rows.append(c)

        print(f"   Condition B: {stats_b['num_claims']} claims -> {stats_b['support_rate_pct']}% Support, {stats_b['contradiction_rate_pct']}% Contradiction")

        summary_rows.append({
            "sample_id": sample_id,
            "language": lang,
            "genre": genre,
            # Condition A stats
            "claims_A": stats_a["num_claims"],
            "support_rate_A": stats_a["support_rate_pct"],
            "contradiction_rate_A": stats_a["contradiction_rate_pct"],
            "neutral_rate_A": stats_a["neutral_rate_pct"],
            # Condition B stats
            "claims_B": stats_b["num_claims"],
            "support_rate_B": stats_b["support_rate_pct"],
            "contradiction_rate_B": stats_b["contradiction_rate_pct"],
            "neutral_rate_B": stats_b["neutral_rate_pct"],
            "verified_at": datetime.now().isoformat(),
        })

    # Save outputs
    output_detailed.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(detailed_rows).to_csv(output_detailed, index=False, encoding="utf-8-sig")
    sum_df = pd.DataFrame(summary_rows)
    sum_df.to_csv(output_summary, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETED!")
    print(f"Detailed claim audits: {output_detailed}")
    print(f"Scorecard summary:    {output_summary}")
    print("=" * 60)

    # Print Aggregate Comparison by Condition
    print("\n--- OVERALL COMPARISON (Condition A vs. Condition B) ---")
    avg_support_a = sum_df["support_rate_A"].mean()
    avg_contra_a = sum_df["contradiction_rate_A"].mean()
    avg_support_b = sum_df["support_rate_B"].mean()
    avg_contra_b = sum_df["contradiction_rate_B"].mean()

    print(f"Condition A (Standard):         Support Rate = {avg_support_a:.1f}% | Contradiction Rate = {avg_contra_a:.1f}%")
    print(f"Condition B (Factuality-Aware): Support Rate = {avg_support_b:.1f}% | Contradiction Rate = {avg_contra_b:.1f}%")
    print("--------------------------------------------------------")

    print("\n--- BREAKDOWN BY LANGUAGE (Section 14) ---")
    for lang, grp in sum_df.groupby("language"):
        sup_a = grp["support_rate_A"].mean()
        sup_b = grp["support_rate_B"].mean()
        con_a = grp["contradiction_rate_A"].mean()
        con_b = grp["contradiction_rate_B"].mean()
        print(f"[{lang.upper()} - {len(grp)} sample(s)]")
        print(f"   Condition A (Standard):         Support = {sup_a:.1f}% | Contradiction = {con_a:.1f}%")
        print(f"   Condition B (Factuality-Aware): Support = {sup_b:.1f}% | Contradiction = {con_b:.1f}%")
    print("--------------------------------------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="FactIndic Phase 4: Verification Pipeline")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/summaries_baseline_A_B.csv"),
        help="Input summaries CSV",
    )
    parser.add_argument(
        "--output_detailed",
        type=Path,
        default=Path("data/claims_verification_detailed.csv"),
        help="Path for detailed claim-by-claim audit CSV",
    )
    parser.add_argument(
        "--output_summary",
        type=Path,
        default=Path("data/verification_summary_report.csv"),
        help="Path for summary-level comparison CSV",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of sample documents to verify (e.g. --limit 5)",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=3,
        help="Top-k evidence sentences to retrieve per claim",
    )

    args = parser.parse_args()
    run_verification_pipeline(
        input_csv=args.input,
        output_detailed=args.output_detailed,
        output_summary=args.output_summary,
        limit=args.limit,
        top_k=args.top_k,
    )

if __name__ == "__main__":
    main()
