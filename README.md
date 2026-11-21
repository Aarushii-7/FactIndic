# FactIndic: Factuality-Aware Summarization for Indic and Code-Mixed Languages

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![PyTorch MPS](https://img.shields.io/badge/PyTorch-Apple%20Silicon%20MPS-green.svg)](https://pytorch.org/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Transformers-yellow.svg)](https://huggingface.co/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

FactIndic is an end-to-end factuality-aware summarization and verification system for Indic languages (Hindi), English, and Indic-English code-mixed text (Hinglish). It investigates whether **NLI-guided, dependency-aware targeted revision (Condition C)** can detect and correct hallucinations compared to standard prompting alone (**Condition A**) and factuality-aware prompting (**Condition B**).

---

## Architecture Overview

```
                                [Input Documents]
                                       │
                         [Unified Dataset Standardization]
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
             [Condition A: Standard]        [Condition B: Factuality-Aware]
                      │                                 │
                      └────────────────┬────────────────┘
                                       │
                          [1. Atomic Claim Extraction]
                                       │
                        [2. Top-k Evidence Retrieval]
                     (Sentence-Transformers Cosine Sim)
                                       │
                       [3. Multilingual NLI Verification]
                             (mDeBERTa-v3-base-xnli)
                                       │
                        [4. Acceptance Policy Decision]
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
           Meets 3 Criteria?                   Fails Policy Criteria?
             [✓ ACCEPTED]                                 │
                                                [5. Claim Graph (Approach C)]
                                                (NetworkX Entity Dependencies)
                                                          │
                                                [6. Targeted Revision (S1/S2)]
                                                (Local Qwen / Gemini with Evidence)
                                                          │
                                                [7. Full Re-Verification]
                                                          │
                                            ┌─────────────┴─────────────┐
                                            ▼                           ▼
                                    [✓ ACCEPTED]              [✗ Flagged for Human Review]
                                                             (Max 2 attempts reached)
```

---

## Three Experimental Conditions

1. **Condition A (Standard Prompt, No Revision)**: Standard concise summarization instruction.
2. **Condition B (Factuality-Aware Prompt, No Revision)**: Explicit instructions restricting output to source-supported facts, preserving named entities, numbers, and dates.
3. **Condition C (Targeted Revision Loop with Claim Graph)**: NLI-guided targeted revision of problematic claim clusters using source evidence, bounded to a maximum of two revision attempts ($S_0 \rightarrow S_1 \rightarrow S_2$).

---

## Acceptance Policy & Decision Rules

A summary is automatically accepted **only** if all three criteria are satisfied:
1. **Factual Support Rate $\ge 90\%$** ($\text{Entailment} / \text{Total Claims} \times 100$)
2. **Contradiction Rate $\le 5\%$** ($\text{Contradiction} / \text{Total Claims} \times 100$)
3. **No High-Confidence Contradictions** ($\text{prob}_{\text{contradiction}} < 0.70$)
4. **Non-Zero Claims**: If zero claims are extracted, support rate is undefined; the summary is rejected.

Summaries failing any criterion enter the **Targeted Revision Loop**. Summaries remaining unresolved after two iterations are marked as `UNRESOLVED_FLAGGED` and terminated automatically by policy.

---

## Repository Structure

```
factIndic/
├── README.md                           # Comprehensive documentation & execution guide
├── requirements.txt                    # Pinned Python dependencies
├── DATASET_INVENTORY.md                # Dataset provenance and candidate statistics
├── dataset_inspection.py               # Downloads and filters ILSUM 2.0
├── select_ilsum_samples.py             # Deterministically samples 150 Hindi & 150 English
├── select_gupshup_samples.py           # Deterministically samples 200 Hinglish validation pairs
├── create_unified_candidates.py        # Normalizes 500 samples into single schema
├── generate_summaries_local.py         # Phase 3: Local LLM runner (Apple Silicon MPS / CUDA)
├── generate_summaries.py               # Phase 3: Gemini API alternative with exponential backoff
├── run_verification.py                 # Phase 4: NLI Verification Pipeline (Support & Contradiction)
├── run_revision_pipeline.py            # Phase 5: Condition C Targeted Revision Loop
├── evaluate_study.py                   # Phase 6: Master Evaluation Suite (ROUGE, Compression, Slices)
│
├── src/                                # Core Modular Engine
│   ├── __init__.py
│   ├── acceptance_policy.py            # 3-rule policy & zero-claim handler
│   ├── claim_extractor.py              # Atomic factual claim splitter
│   ├── claim_graph.py                  # NetworkX dependency graph (Approach C)
│   ├── evidence_retriever.py           # Multilingual sentence embedding & cosine top-k
│   ├── metrics.py                      # Pure-Python ROUGE-1/2/L & compression engine
│   ├── nli_verifier.py                 # mDeBERTa-v3 multilingual NLI classifier
│   └── revision.py                     # Targeted revision prompt & editor
│
└── data/                               # Experimental Artifacts & Outputs
    ├── candidates_master.csv           # 500 normalized candidate records
    ├── summaries_baseline_A_B.csv      # Baseline Condition A & B outputs
    ├── claims_verification_detailed.csv# Claim-by-claim NLI audits
    ├── verification_summary_report.csv # Baseline verification scorecard
    ├── condition_c_final_summaries.csv # Final Condition A vs. B vs. C comparison
    ├── revision_audit_trail.csv        # Step-by-step revision history (S0 -> S1 -> S2)
    ├── evaluation_master_metrics.csv   # Comprehensive metric matrix
    ├── evaluation_summary_by_condition.csv # Master scorecard
    ├── evaluation_language_breakdown.csv   # Language-sliced breakdown
    └── EVALUATION_REPORT.md            # Markdown research report
```

---

## Installation & Setup

### Prerequisites
- Python 3.11 (`python3.11`)
- macOS with Apple Silicon (M1/M2/M3/M4) recommended for fast local MPS acceleration, or Linux/Windows with CUDA.

### Setup Instructions

```bash
# 1. Clone the repository
git clone <repo-url>
cd factIndic

# 2. Create and activate a Python 3.11 virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Upgrade pip and install all dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step-by-Step Execution Guide

### Step 1: Dataset Preparation & Harmonization (Phase 1 & 2)

```bash
# Filter and inspect ILSUM datasets
python dataset_inspection.py

# Deterministically sample candidate pairs (random_state=42)
python select_ilsum_samples.py
python select_gupshup_samples.py

# Unify schemas into data/candidates_master.csv (500 samples)
python create_unified_candidates.py
```

### Step 2: Generate Baseline Summaries (Phase 3)

Run Condition A (Standard) and Condition B (Factuality-Aware) locally on your Mac's GPU:

```bash
# Process a balanced pilot slice (5 Hindi, 5 English, 5 Hinglish = 15 samples)
python generate_summaries_local.py --balanced 5

# Or run on the full candidate dataset:
python generate_summaries_local.py --limit 0
```
*Outputs are saved incrementally to `data/summaries_baseline_A_B.csv`.*

### Step 3: Run Verification Pipeline (Phase 4)

Audits each summary by extracting atomic claims, retrieving evidence sentences, and running multilingual NLI:

```bash
# Verify baseline summaries
python run_verification.py
```
*Outputs:*
- `data/claims_verification_detailed.csv` (Detailed audit trail per claim)
- `data/verification_summary_report.csv` (Scorecard of Support and Contradiction rates)

### Step 4: Run Targeted Revision Loop (Phase 5 - Condition C)

Applies the 3 acceptance rules, builds NetworkX claim graphs, revises problematic claims using retrieved evidence, and re-verifies:

```bash
# Execute revision loop (maximum 2 attempts)
python run_revision_pipeline.py --limit 18
```
*Outputs:*
- `data/condition_c_final_summaries.csv` (Condition A vs. B vs. C side-by-side)
- `data/revision_audit_trail.csv` (Full trace of steps $S_0 \rightarrow S_1 \rightarrow S_2$)

### Step 5: Comprehensive Evaluation Suite (Phase 6)

Computes ROUGE-1/2/L, compression ratios, language slices, and decision distributions:

```bash
python evaluate_study.py
```
*Generates publication-ready reports in `data/EVALUATION_REPORT.md` and CSV summary tables.*

---

## Key Experimental Results

Evaluated on an 18-document balanced testbed (8 Hindi news, 5 English news, 5 Hinglish dialogues):

### 1. Overall Performance Across Conditions (Core Metrics)

#### A. Lexical Overlap Metrics (ROUGE with Reference Summaries)
*Reference Summaries:* ILSUM 2.0 (Hindi/English) & GupShup (Hinglish). Evaluated per document and macro-averaged across samples.

| Metric | Condition A (Standard) | Condition B (Factuality-Aware) | Condition C (Targeted Revision) | Net Delta (C vs. A) |
| :--- | :---: | :---: | :---: | :---: |
| **ROUGE-1 Precision** | 0.3107 | 0.2292 | **0.2104** | -0.1003 |
| **ROUGE-1 Recall** | 0.2844 | 0.2468 | **0.2732** | -0.0112 |
| **ROUGE-1 $F_1$** | 0.2535 | 0.1951 | **0.2126** | -0.0409 |
| **ROUGE-2 $F_1$** | 0.0986 | 0.0583 | **0.0687** | -0.0299 |
| **ROUGE-L $F_1$** | 0.1946 | 0.1477 | **0.1525** | -0.0421 |
| **Average Summary Words** | 52.4 words | 59.1 words | 56.0 words | +3.6 words |
| **Compression Ratio (words)** | 27.47% | 27.80% | 27.79% | +0.32% |
| **Inference Latency** | 21.88s | 40.29s | 49.04s | +27.16s |

#### B. Factuality & NLI Verification Metrics (Macro-Average vs. Micro-Average)
*NLI Model:* `mDeBERTa-v3-base-xnli` with evidence retrieval via `paraphrase-multilingual-MiniLM-L12-v2`.

| Metric / Evaluation Mode | Condition A (Standard) | Condition B (Factuality-Aware) | Condition C (Targeted Revision) | Net Delta (C vs. A) |
| :--- | :---: | :---: | :---: | :---: |
| **Macro Factual Support (%)** | 52.50% | 66.11% | **67.99%** | **+15.49%** |
| **Macro Contradiction (%)** | 14.58% | 12.50% | **9.10%** | **-5.48%** |
| **Micro Support Rate (Claims)** | 30/60 (50.00%) | 39/67 (58.21%) | **38/64 (59.38%)** | **+9.38%** |
| **Micro Contradiction Rate (Claims)** | 8/60 (13.33%) | 8/67 (11.94%) | **6/64 (9.38%)** | **-3.95%** |
| **Total Evaluated Claims ($N$)** | $N = 60$ | $N = 67$ | $N = 64$ | - |

*Note on 127 Baseline Claims:* Pooled baseline claims across Condition A ($N=60$) and Condition B ($N=67$): 69 Entailments ($54.33\%$), 42 Neutrals ($33.07\%$), 16 Contradictions ($12.60\%$).

### 2. Language Breakdown

| Language | Samples | Cond A Support | Cond B Support | Cond C Support | Cond A Contra | Cond B Contra | Cond C Contra |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English News** | 5 | 74.3% | 72.3% | **72.3%** | 5.0% | 3.3% | **3.3%** |
| **Hindi News** | 8 | 58.3% | 53.5% | **57.8%** | 10.9% | 26.0% | **18.4%** |
| **Hinglish Dialogue** | 5 | 21.3% | 80.0% | **80.0%** | 30.0% | 0.0% | **0.0%** |

### 3. Acceptance Policy Decisions
- **Total Evaluated Documents:** 18
- **Accepted Automatically at $S_0$:** 7 (38.9%)
- **Accepted After Targeted Revision ($S_1$):** 1 (5.6%)
- **Total Accepted Summaries:** **8 (44.4%)**
- **Automated Policy Terminated (`UNRESOLVED_FLAGGED`):** **10 (55.6%)**

---

## Research Citations & Models
- **Base Summarization Model:** `Qwen/Qwen2.5-1.5B-Instruct`
- **Evidence Retriever:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Multilingual NLI Classifier:** `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`
- **Datasets:** ILSUM 2.0 (Hindi & English), GupShup (Hinglish-to-English Dialogue)
