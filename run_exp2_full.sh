#!/bin/bash
set -e

# FactIndic: Experiment 2 - Refined Factuality Prompts (Devanagari B2, Hinglish B2, English B2.1)
# Full 500-Sample Pipeline (Hindi, English, Hinglish)
# Runs with native Apple Silicon GPU (MPS) acceleration outside the sandbox.

cd /Users/aarushi/factIndic
source .venv/bin/activate

TARGET_DIR="data/experiments/exp2_refined_factuality"
mkdir -p "$TARGET_DIR"

echo "=========================================================="
echo "STARTING EXPERIMENT 2: FULL 500-SAMPLE PIPELINE"
echo "Target directory: $TARGET_DIR"
echo "Prompt config:    Devanagari B2 (HI) | Code-mixed B2 (Hing) | 2-Sentence Aggregate B2.1 (EN)"
echo "Generator config: Qwen/Qwen2.5-1.5B-Instruct, Seed=42, Temp=0.2, MaxTokens=250"
echo "=========================================================="

# 1. Summary Generation (Conditions A and B for all 500 documents)
echo ""
echo ">>> STEP 1/4: Summary Generation (Conditions A & B)..."
python3 generate_summaries_local.py \
  --input data/candidates_master.csv \
  --output "$TARGET_DIR/summaries_A_B.csv" \
  --seed 42

# 2. Claim Verification (Conditions A and B)
echo ""
echo ">>> STEP 2/4: Claim Verification (Multilingual Retrieval + NLI)..."
python3 run_verification.py \
  --input "$TARGET_DIR/summaries_A_B.csv" \
  --output_detailed "$TARGET_DIR/claims_detailed.csv" \
  --output_summary "$TARGET_DIR/verification_summary.csv"

# 3. Targeted Claim Revision (Condition C)
echo ""
echo ">>> STEP 3/4: Condition C Targeted Revision Loop..."
python3 run_revision_pipeline.py \
  --input "$TARGET_DIR/summaries_A_B.csv" \
  --output_final "$TARGET_DIR/condition_c.csv" \
  --output_audit "$TARGET_DIR/revision_audit.csv" \
  --max_revisions 1

# 4. Comprehensive Evaluation Suite
echo ""
echo ">>> STEP 4/4: Comprehensive Evaluation Suite..."
python3 evaluate_study.py \
  --data_dir "$TARGET_DIR" \
  --output_dir "$TARGET_DIR" \
  --master_csv data/candidates_master.csv \
  --input_baseline "$TARGET_DIR/summaries_A_B.csv" \
  --input_verification "$TARGET_DIR/verification_summary.csv" \
  --input_cond_c "$TARGET_DIR/condition_c.csv" \
  --input_detailed_claims "$TARGET_DIR/claims_detailed.csv" \
  --input_audit "$TARGET_DIR/revision_audit.csv"

echo ""
echo "=========================================================="
echo "EXPERIMENT 2 COMPLETE!"
echo "Summary by Condition: $TARGET_DIR/evaluation_summary_by_condition.csv"
echo "Language Breakdown:   $TARGET_DIR/evaluation_language_breakdown.csv"
echo "Publication Report:   $TARGET_DIR/evaluation_report.md"
echo "=========================================================="
