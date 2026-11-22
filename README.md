# FactIndic: Factuality-Aware Summarization for Indic and Code-Mixed Languages

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![PyTorch MPS](https://img.shields.io/badge/PyTorch-Apple%20Silicon%20MPS-green.svg)](https://pytorch.org/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-Transformers-yellow.svg)](https://huggingface.co/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**FactIndic** is an end-to-end factuality-aware summarization and verification system for Indic languages (**Hindi**), English (**English**), and Indic-English code-mixed text (**Hinglish**). It investigates whether **NLI-guided targeted claim revision (Condition C)** can detect and correct factual hallucinations compared to standard prompting alone (**Condition A**) and precision factuality prompting (**Condition B**).

---

## Architecture Overview

```
                                [Input Documents]
                                       │
                         [500-Sample Balanced Dataset]
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
             [✓ ACCEPTED]                                │
                                               [5. In-Place Targeted Revision]
                                               (Evidence-Constrained Claim Edit)
                                                         │
                                               [6. Full Re-Verification (S1)]
                                                         │
                                           ┌─────────────┴─────────────┐
                                           ▼                           ▼
                                   [✓ ACCEPTED (S1)]         [✗ Flagged for Review]
```

---

## Three Experimental Conditions

1. **Condition A (Standard Prompt, No Revision)**: Standard concise summarization instruction with identical language preservation directives.
2. **Condition B (Factuality-Aware Prompt, No Revision)**: Language-adaptive positive constraints:
   - **Hindi:** Devanagari 9-rule prompt enforcing entity/negation accuracy and brevity (2–3 sentences).
   - **Hinglish (H2E):** Dialogue-to-English translation and summarization prompt.
   - **English:** Structural 2-sentence format prioritizing primary events and aggregate numerical figures over granular breakdowns.
3. **Condition C (Targeted Revision Loop)**: NLI-guided targeted revision of problematic claims using retrieved evidence sentences, bounded to a single revision attempt ($S_0 \rightarrow S_1$).

---

## Acceptance Policy & Decision Rules

A summary is automatically accepted **only** if all criteria are satisfied:
1. **Factual Support Rate $\ge 90\%$** ($\text{Entailment} / \text{Total Claims} \times 100$)
2. **Contradiction Rate $\le 5\%$** ($\text{Contradiction} / \text{Total Claims} \times 100$)
3. **No High-Confidence Contradictions** ($\text{prob}_{\text{contradiction}} < 0.70$)
4. **Non-Zero Claims**: If zero claims are extracted, support rate is undefined; the summary is rejected.

Summaries failing any criterion enter the **Targeted Revision Loop**. Unresolved summaries after revision are marked as `UNRESOLVED_FLAGGED` and terminated automatically by policy.

---

## Clean Repository Structure

```
factIndic/
├── README.md                           # Documentation & benchmark report
├── requirements.txt                    # Pinned Python dependencies
├── run_exp2_full.sh                    # End-to-end executable pipeline runner
├── generate_summaries_local.py         # Summary generation (Conditions A & B)
├── run_verification.py                 # Claim extraction & multilingual NLI verification
├── run_revision_pipeline.py            # Condition C targeted revision pipeline
├── evaluate_study.py                   # Master evaluation suite (ROUGE, NLI, Compression)
│
├── src/                                # Core Algorithmic Engine
│   ├── __init__.py
│   ├── acceptance_policy.py            # 3-rule policy & zero-claim handler
│   ├── claim_extractor.py              # Atomic factual claim splitter
│   ├── claim_graph.py                  # Entity dependency graph
│   ├── evidence_retriever.py           # Multilingual sentence embedding & cosine top-k
│   ├── metrics.py                      # Pure-Python ROUGE-1/2/L & compression engine
│   ├── nli_verifier.py                 # mDeBERTa-v3 multilingual NLI classifier
│   └── revision.py                     # In-place evidence-based claim reviser
│
├── data/                               # Experimental Data & Artifacts
│   ├── candidates_master.csv           # 500 normalized balanced candidate records
│   ├── experiments/
│   │   └── exp2_refined_factuality/    # Finalized 500-sample outputs & evaluation reports
│   ├── gupshup/                        # Raw GupShup dialogue dataset
│   ├── ilsum/                          # Raw ILSUM 2.0 Hindi/English dataset
│   └── mutant/                         # Raw mutant benchmark dataset
│
└── docs/                               # Academic Publications & Presentations
    ├── PRESENTATION_SLIDES.md          # Defense & presentation slides
    └── RESEARCH_PAPER_IEEE.md          # IEEE formatted research paper draft
```

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd factIndic

# 2. Create and activate a Python 3.11 virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Execution Guide

### Run Full 500-Sample Pipeline (Native GPU Acceleration)
```bash
./run_exp2_full.sh
```

### Or Run Individual Stages
```bash
# 1. Summary Generation (Conditions A and B)
python3 generate_summaries_local.py --input data/candidates_master.csv --output data/experiments/exp2_refined_factuality/summaries_A_B.csv --seed 42

# 2. Claim Verification
python3 run_verification.py --input data/experiments/exp2_refined_factuality/summaries_A_B.csv --output_detailed data/experiments/exp2_refined_factuality/claims_detailed.csv --output_summary data/experiments/exp2_refined_factuality/verification_summary.csv

# 3. Condition C Targeted Revision
python3 run_revision_pipeline.py --input data/experiments/exp2_refined_factuality/summaries_A_B.csv --output_final data/experiments/exp2_refined_factuality/condition_c.csv --output_audit data/experiments/exp2_refined_factuality/revision_audit.csv --max_revisions 1

# 4. Master Evaluation Suite
python3 evaluate_study.py --data_dir data/experiments/exp2_refined_factuality/ --output_dir data/experiments/exp2_refined_factuality/
```

---

## Full Experimental Results (500 Documents)

### 1. Overall Performance Across Conditions

| Metric | Condition A (Standard) | Condition B (Factuality-Aware) | Condition C (Targeted Revision) | Net Delta (C vs. A) |
| :--- | :---: | :---: | :---: | :---: |
| **Macro Factual Support (%)** | 62.30% | 61.86% | **81.40%** | **+19.10%** |
| **Macro Contradiction (%)** | 11.66% | 11.00% | **4.83%** | **-6.83%** |
| **Micro Support Rate (Claims)** | 64.41% (1,296 / 2,012) | 62.12% (1,161 / 1,869) | **82.10% (1,220 / 1,486)** | **+17.69%** |
| **Micro Contradiction Rate (Claims)** | 11.33% (228 / 2,012) | 11.66% (218 / 1,869) | **4.64% (69 / 1,486)** | **-6.69%** |
| **Strict Acceptance Rate (%)** | 23.60% (118 / 500) | 24.60% (123 / 500) | **62.60% (313 / 500)** | **+39.00%** |
| **Average Summary Length** | 57.9 words | 57.6 words | **46.1 words** | -11.8 words |
| **ROUGE-L Precision** | 0.2552 | 0.2635 | **0.2862** | +0.0310 |
| **ROUGE-L F1-Score** | 0.3170 | **0.3250** | 0.2999 | -0.0171 |

### 2. Language Breakdown (Section 14)

| Language | Partition Size | Cond A Support | Cond B Support | Cond C Support | Cond A Contra | Cond B Contra | Cond C Contra | Strict Acceptance (C) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Hindi** (`ILSUM_HI`) | 150 | 61.77% | 65.83% | **92.98%** | 18.23% | 15.64% | **3.24%** | **90.67%** (136/150) |
| **Hinglish** (`GupShup` H2E) | 200 | 54.93% | 56.91% | **77.17%** | 9.32% | 9.56% | **5.20%** | **53.00%** (106/200) |
| **English** (`ILSUM_EN`) | 150 | 72.66% | 64.48% | **75.45%** | 8.22% | 8.28% | **5.92%** | **47.33%** (71/150) |

### 3. Policy Acceptance Decisions
- **Total Audited Documents:** 500
- **Accepted Automatically at $S_0$ (Direct from B):** 123 (24.6%)
- **Accepted After Targeted Revision ($S_1$):** 190 (38.0%)
- **Total Accepted Summaries:** **313 (62.6%)**
- **Flagged for Human Review (`UNRESOLVED_FLAGGED`):** 187 (37.4%)

---

## Models & Tools
- **Generative Summarizer:** `Qwen/Qwen2.5-1.5B-Instruct`
- **Evidence Retriever:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Multilingual NLI Classifier:** `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`
- **Datasets:** ILSUM 2.0 (Hindi/English News), GupShup (Hinglish-to-English Dialogue)
