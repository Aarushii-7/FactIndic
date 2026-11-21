# FactIndic: Comprehensive Experimental Evaluation Report (Phase 6)
**Date Generated:** 2026-11-21 18:07:11  
**Study Setup:** 3 Experimental Conditions (A: Standard, B: Factuality-Aware, C: NLI-Guided Revision Loop)  
**Sample Corpus:** 18 Evaluated Documents (8 Hindi News, 5 English News, 5 Hinglish Dialogues)

---

## 1. Overall Performance Across Experimental Conditions (CSET 346 Core Metrics)

### A. Lexical Overlap Metrics (ROUGE with Reference Summaries)
*Ground Truth:* Standard reference summaries from ILSUM 2.0 (Hindi/English) and GupShup (Hinglish). Evaluated per document and macro-averaged across samples.

| Metric | Condition A (Standard) | Condition B (Factuality-Aware) | Condition C (Revision Loop) | Net Delta (C vs. A) |
| :--- | :---: | :---: | :---: | :---: |
| **Precision** | 0.3107 | 0.2292 | **0.2104** | -0.1003 |
| **Recall** | 0.2844 | 0.2468 | **0.2732** | -0.0112 |
| **F1-Score** | 0.2535 | 0.1951 | **0.2126** | -0.0409 |
| **Average Summary Length** | 52.4 words | 59.1 words | 56.0 words | - |
| **Compression Ratio (%)** | 27.47% | 27.8% | 27.79% | - |
| **Inference Time (s)** | 21.88s | 40.29s | 49.04s | - |
| **Factual Support (%)** | **52.5%** | **66.11%** | **67.99%** | **+15.5%** |
| **Contradiction (%)** | **14.58%** | **12.5%** | **9.1%** | **-5.5%** |

---

### B. Factuality & NLI Verification Metrics (Macro-Average vs. Micro-Average)
*NLI Model:* `MoritzLaurer/mDeBERTa-v3-base-xnli` with evidence retrieval via `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

- **Macro-Average (Document-Level):** Evaluates factuality per document, then computes the mean across all 18 documents.
- **Micro-Average (Claim-Level):** Pools all extracted claims in that condition and reports exact counts: Rate = (Target Claims / Total Audited Claims) * 100%.

| Metric / Evaluation Mode | Condition A (Standard) | Condition B (Factuality-Aware) | Condition C (Revision Loop) | Net Delta (C vs. A) |
| :--- | :---: | :---: | :---: | :---: |
| **Macro Factual Support Rate (%)** | **52.5%** | **66.11%** | **67.99%** | **+15.5%** |
| **Macro Contradiction Rate (%)** | **14.58%** | **12.5%** | **9.1%** | **-5.5%** |
| **Micro Support Rate (Claims)** | f"30/60 (50.0%)" | f"39/67 (58.21%)" | **f"38/64 (59.38%)"** | **+9.4%** |
| **Micro Contradiction Rate (Claims)** | f"8/60 (13.33%)" | f"8/67 (11.94%)" | **f"6/64 (9.38%)"** | **-3.9%** |
| **Total Claims Audited (N)** | N = 60 claims | N = 67 claims | N = 64 claims | - |

*Note on 127 Baseline Claims:* The 127 baseline claims in `claims_verification_detailed.csv` represent the pooled claims across Condition A (N = 60) and Condition B (N = 67). Across all 127 baseline claims:
- **Baseline Entailment:** 69 / 127 = 54.33%
- **Baseline Neutral:** 42 / 127 = 33.07%
- **Baseline Contradiction:** 16 / 127 = 12.6%

---

## 2. Language Slice Analysis (Section 14)

| Language | Samples | Precision | Recall | F1-Score | Length | Compression (%) | Inference (s) | Support (%) | Contradiction (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ENGLISH** | 5 | 0.2074 | 0.4033 | 0.2723 | 74.4 words | 22.29% | 13.95s | 72.33% | 3.33% |
| **HINDI** | 8 | 0.1583 | 0.1059 | 0.1062 | 59.1 words | 15.5% | 96.66s | 57.78% | 18.4% |
| **HINGLISH** | 5 | 0.2968 | 0.4109 | 0.3232 | 32.6 words | 52.97% | 7.94s | 80.0% | 0.0% |

---

## 3. Policy Acceptance & Decision Distribution (Section 12)

Strict Automated Acceptance Policy: Support Rate >= 90%, Contradiction Rate <= 5%, and No High-Confidence Contradictions (p >= 0.70).

- **Total Documents Audited:** 18
- **Accepted Automatically at S0:** 7 (38.9%)
- **Accepted After Targeted Revision (S1):** 1 (5.6%)
- **Total Accepted Summaries:** **8 (44.4%)**
- **Automated Policy Flagged / Unresolved (`UNRESOLVED_FLAGGED`):** **10 (55.6%)**

---

## 4. Key Scientific Findings & Discussion
1. **Targeted Revision Enhances Faithfulness**: Condition C achieved the highest factual support rate (**67.99%** Macro / **59.38%** Micro) and reduced contradictions down to **9.1%** Macro / **9.38%** Micro.
2. **Breakthrough on Code-Mixed Hinglish**: Condition A suffered from extreme factual inversion on code-mixed dialogue (30.0% contradiction rate). Factuality-aware prompting and verification eliminated contradictions down to **0.0%** and quadrupled the support rate.
3. **Safety Through Bounded Revision**: The 3-rule policy with bounded revision (k=2) prevented runaway loops while safely terminating revisions for documents with unresolved source ambiguities.
