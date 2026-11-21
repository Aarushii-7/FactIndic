"""
FactIndic - Phase 5: Condition C (NLI-Guided Targeted Revision Loop) Runner
Implements the 3 critical implementation decisions:
1. High-confidence contradiction thresholding (prob_contradiction >= threshold).
2. Explicit handling of zero-claim edge cases.
3. Full re-verification after each revision attempt, bounded to a maximum of 2 attempts,
   terminating revisions automatically when summaries cannot be resolved within bounds.
"""

import argparse
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from src.evidence_retriever import EvidenceRetriever
from src.claim_extractor import ClaimExtractor
from src.nli_verifier import NLIVerifier
from src.acceptance_policy import AcceptancePolicy
from src.claim_graph import ClaimGraph
from src.revision import TargetedReviser

def load_qwen_pipe(model_id: str = "Qwen/Qwen2.5-1.5B-Instruct"):
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"\nLoading local Qwen model ({model_id}) on {device} for targeted revision...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    dtype = torch.float16 if device in ["mps", "cuda"] else torch.float32
    try:
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype)
        model.to(torch.device(device))
    except Exception:
        device = "cpu"
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32)
        model.to(torch.device("cpu"))
    model.eval()

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    print("Qwen revision model ready!\n")
    return pipe

def verify_summary(
    summary_text: str,
    source_text: str,
    genre: str,
    extractor: ClaimExtractor,
    retriever: EvidenceRetriever,
    verifier: NLIVerifier,
    policy: AcceptancePolicy,
    top_k: int = 3,
):
    """Audits all claims in a summary and evaluates acceptance criteria."""
    claims = extractor.extract_claims(summary_text)

    # Decision 2: Zero claims check
    if len(claims) == 0:
        eval_result = policy.evaluate([])
        return [], eval_result

    claim_records = []
    for c in claims:
        cid = c["claim_id"]
        ctext = c["claim_text"]

        retrieved = retriever.retrieve(ctext, source_text, genre=genre, top_k=top_k)
        evidence_text = " ".join([r["sentence"] for r in retrieved])
        avg_sim = (
            round(sum([r["score"] for r in retrieved]) / len(retrieved), 4)
            if retrieved else 0.0
        )

        nli_res = verifier.verify(premise=evidence_text, hypothesis=ctext)

        claim_records.append({
            "claim_id": cid,
            "claim_text": ctext,
            "retrieved_evidence": evidence_text,
            "retrieval_similarity": avg_sim,
            "nli_label": nli_res["label"],
            "confidence": nli_res["confidence"],
            "prob_entailment": nli_res["probabilities"].get("entailment", 0.0),
            "prob_contradiction": nli_res["probabilities"].get("contradiction", 0.0),
            "prob_neutral": nli_res["probabilities"].get("neutral", 0.0),
        })

    eval_result = policy.evaluate(claim_records)
    return claim_records, eval_result

def run_condition_c(
    input_csv: Path,
    output_final_csv: Path,
    output_audit_csv: Path,
    limit: int = None,
    max_revisions: int = 2,
    high_conf_thresh: float = 0.70,
):
    print("=" * 65)
    print("FACTINDIC - PHASE 5: CONDITION C (TARGETED REVISION LOOP)")
    print("=" * 65)

    # 1. Initialize models & engines
    policy = AcceptancePolicy(
        support_threshold=90.0,
        contradiction_threshold=5.0,
        high_confidence_threshold=high_conf_thresh,
    )
    retriever = EvidenceRetriever()
    verifier = NLIVerifier()
    qwen_pipe = load_qwen_pipe()
    extractor = ClaimExtractor(pipe=None)  # clean sentence-level claim decomposition
    reviser = TargetedReviser(pipe=qwen_pipe)

    df = pd.read_csv(input_csv)
    if limit is not None and limit > 0:
        df = df.head(limit)

    total = len(df)
    final_records = []
    audit_trail = []

    print(f"\nProcessing {total} documents through Condition C Pipeline...")

    for idx, row in df.iterrows():
        sample_id = row["sample_id"]
        lang = row.get("language", "unknown")
        genre = row.get("genre", "news")
        source_text = str(row["source_text"])
        initial_summary = str(row.get("summary_B_factuality", ""))

        print(f"\n[{idx+1}/{total}] Processing {sample_id} ({lang}, {genre})...")

        current_summary = initial_summary
        attempt = 0
        status = "PENDING"
        initial_eval = None

        while attempt <= max_revisions:
            step_name = f"S{attempt}"
            claims, eval_res = verify_summary(
                summary_text=current_summary,
                source_text=source_text,
                genre=genre,
                extractor=extractor,
                retriever=retriever,
                verifier=verifier,
                policy=policy,
            )

            if attempt == 0:
                initial_eval = eval_res

            # Log audit step
            audit_trail.append({
                "sample_id": sample_id,
                "step": step_name,
                "summary_text": current_summary,
                "total_claims": eval_res.get("total_claims", 0),
                "support_rate": eval_res["support_rate"],
                "contradiction_rate": eval_res["contradiction_rate"],
                "status": eval_res["status"],
                "accepted": eval_res["accepted"],
                "reasons": " | ".join(eval_res["reasons"]),
            })

            print(f"   [{step_name}] Support={eval_res['support_rate']}% | Contra={eval_res['contradiction_rate']}% | Status: {eval_res['status']}")

            # Decision: Check if accepted
            if eval_res["accepted"]:
                status = f"ACCEPTED_AT_{step_name}"
                print(f"   ✓ Summary accepted at {step_name}!")
                break

            # If rejected and attempts remaining, trigger revision
            if attempt < max_revisions:
                attempt += 1
                flagged_ids = [c["claim_id"] for c in eval_res["flagged_claims"]]

                # Build Claim Graph (Approach C)
                graph = ClaimGraph(claims)
                related_info = graph.get_related_claims(flagged_ids)

                print(f"   -> Revision #{attempt}: Revising {len(flagged_ids)} flagged claim(s) + {len(related_info['dependent_ids'])} dependent claim(s)...")

                # Generate revised summary
                current_summary = reviser.revise(
                    source_text=source_text,
                    current_summary=current_summary,
                    graph_context=related_info,
                )
            else:
                # Decision 3: Max revision attempts reached
                status = "UNRESOLVED_FLAGGED"
                print(f"   ✗ Max revision attempts ({max_revisions}) reached. Policy terminated (unresolved).")
                break

        final_records.append({
            "sample_id": sample_id,
            "language": lang,
            "genre": genre,
            "source_text": source_text,
            "summary_A_standard": row.get("summary_A_standard", ""),
            "summary_B_factuality": initial_summary,
            "summary_C_revised": current_summary,
            "final_status": status,
            "revision_attempts_used": attempt,
            "initial_support_rate": initial_eval["support_rate"] if initial_eval else 0.0,
            "final_support_rate": eval_res["support_rate"],
            "initial_contra_rate": initial_eval["contradiction_rate"] if initial_eval else 0.0,
            "final_contra_rate": eval_res["contradiction_rate"],
            "completed_at": datetime.now().isoformat(),
        })

    # Save outputs
    output_final_csv.parent.mkdir(parents=True, exist_ok=True)
    final_df = pd.DataFrame(final_records)
    final_df.to_csv(output_final_csv, index=False, encoding="utf-8-sig")

    pd.DataFrame(audit_trail).to_csv(output_audit_csv, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 65)
    print("PHASE 5: REVISION PIPELINE COMPLETE!")
    print(f"Final summaries: {output_final_csv}")
    print(f"Audit history:   {output_audit_csv}")
    print("=" * 65)

    # Print 3-Condition Final Scorecard
    print("\n--- 3-WAY CONDITION COMPARISON (A vs. B vs. C) ---")
    b_sup = final_df["initial_support_rate"].mean()
    b_con = final_df["initial_contra_rate"].mean()
    c_sup = final_df["final_support_rate"].mean()
    c_con = final_df["final_contra_rate"].mean()

    print(f"Condition B (Before Revision - S0): Support = {b_sup:.1f}% | Contradiction = {b_con:.1f}%")
    print(f"Condition C (After Revision Loop):  Support = {c_sup:.1f}% | Contradiction = {c_con:.1f}%")

    accepted_count = sum(1 for s in final_df["final_status"] if s.startswith("ACCEPTED"))
    unresolved_count = sum(1 for s in final_df["final_status"] if s in ["NEEDS_REVIEW", "UNRESOLVED_FLAGGED"])
    print(f"\nPolicy Decisions: {accepted_count}/{total} Accepted | {unresolved_count}/{total} Policy Terminated (Unresolved)")
    print("---------------------------------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="FactIndic Phase 5: Condition C Revision Loop")
    parser.add_argument("--input", type=Path, default=Path("data/summaries_baseline_A_B.csv"))
    parser.add_argument("--output_final", type=Path, default=Path("data/condition_c_final_summaries.csv"))
    parser.add_argument("--output_audit", type=Path, default=Path("data/revision_audit_trail.csv"))
    parser.add_argument("--limit", type=int, default=5, help="Number of documents to run through revision (default: 5)")
    parser.add_argument("--max_revisions", type=int, default=2, help="Max revision attempts (default: 2)")
    parser.add_argument("--high_conf_thresh", type=float, default=0.70, help="Confidence threshold for high-confidence contradiction")

    args = parser.parse_args()
    run_condition_c(
        input_csv=args.input,
        output_final_csv=args.output_final,
        output_audit_csv=args.output_audit,
        limit=args.limit,
        max_revisions=args.max_revisions,
        high_conf_thresh=args.high_conf_thresh,
    )

if __name__ == "__main__":
    main()
