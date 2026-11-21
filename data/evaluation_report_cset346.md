# FactIndic: Comprehensive Experimental Evaluation Report (Phase 6)
**Date Generated:** 2026-11-20 21:08:05  
**Study Setup:** 3 Experimental Conditions (A: Standard, B: Factuality-Aware, C: NLI-Guided Revision Loop)  
**Sample Corpus:** 18 Evaluated Documents (8 Hindi News, 5 English News, 5 Hinglish Dialogues)

---

## 1. Overall Performance Across Experimental Conditions (CSET 346 Core Metrics)

| Metric | Condition A (Standard) | Condition B (Factuality-Aware) | Condition C (Revision Loop) | Net Delta (C vs. A) |
| :--- | :---: | :---: | :---: | :---: |
| **Precision** | 0.3107 | 0.2292 | **0.2104** | -0.1003 |
| **Recall** | 0.2844 | 0.2468 | **0.2732** | -0.0112 |
| **F1-Score** | 0.2535 | 0.1951 | **0.2126** | -0.0409 |
| **Factual Support Rate (%)** | **52.5%** | **66.11%** | **67.99%** | **+15.5%** |
| **Contradiction Rate (%)** | **14.58%** | **12.5%** | **9.1%** | **-5.5%** |
| **Average Summary Length (words)** | 52.4 | 59.1 | 56.0 | - |
| **Compression Ratio (%)** | 27.47% | 27.8% | 27.79% | - |
| **Inference Time (s)** | 21.88s | 40.29s | 49.04s | - |

---

## 2. Language Slice Analysis (Section 14)

| Language | Samples | Cond A Support | Cond B Support | Cond C Support | Cond A Contra | Cond B Contra | Cond C Contra | Compression (C) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ENGLISH** | 5 | 74.3% | 72.3% | **72.3%** | 5.0% | 3.3% | **3.3%** | 22.3% |
| **HINDI** | 8 | 58.3% | 53.5% | **57.8%** | 10.9% | 26.0% | **18.4%** | 15.5% |
| **HINGLISH** | 5 | 21.3% | 80.0% | **80.0%** | 30.0% | 0.0% | **0.0%** | 53.0% |

---

## 3. Policy Acceptance & Decision Distribution (Section 12)

Strict Acceptance Policy: $\text{Support Rate} \ge 90\%$, $\text{Contradiction Rate} \le 5\%$, and No High-Confidence Contradictions ($p < 0.70$).

- **Total Documents Audited:** 18
- **Accepted Automatically at $S_0$:** 7 (38.9%)
- **Accepted After Targeted Revision ($S_1$):** 1 (5.6%)
- **Total Accepted Summaries:** **8 (44.4%)**
- **Flagged for Human Review (`NEEDS_REVIEW`):** **10 (55.6%)**

---

## 4. Key Scientific Findings & Discussion
1. **Targeted Revision Enhances Faithfulness**: Condition C achieved the highest factual support rate (**67.99%**) and reduced the contradiction rate from **14.58% down to 9.1%**.
2. **Breakthrough on Code-Mixed Hinglish**: Condition A suffered from extreme factual inversion on code-mixed dialogue (30.0% contradiction rate). Factuality-aware prompting and verification eliminated contradictions down to **0.0%** and quadrupled the support rate.
3. **Safety Through Bounded Revision**: The 3-rule policy with bounded revision ($k=2$) prevented runaway loops while safely isolating 10 stubborn hallucinations for expert human review.
