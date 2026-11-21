# FactIndic: Factuality-Aware Summarization for Indic and Code-Mixed Languages
## Presentation Slide Deck & Defense Outline
**Course:** CSET 346 – Natural Language Processing  
**Instructor:** Dr. Geetanjali Singh | Bennett University  
**Student Presenter:** Aarushi  

---

### Slide 1: Title & Overview
- **Header:** FactIndic: Factuality-Aware Summarization & Targeted Revision for Indic and Code-Mixed Languages
- **Subtitle:** Investigating Factual Consistency in Hindi, English, and Romanized Hinglish
- **Author:** Aarushi (Bennett University)
- **Course & Instructor:** CSET 346 (Dr. Geetanjali Singh)
- **Speaker Notes:**
  > "Good morning Dr. Singh. Today I am presenting FactIndic, an end-to-end factuality-aware summarization and verification system for Indic and code-mixed languages. Modern LLMs generate remarkably fluent summaries, but they often hallucinate entities, invert polarities, or alter numbers—especially in low-resource Indic text and informal Hinglish. FactIndic provides a complete automated pipeline to detect, verify, and surgically correct these hallucinations."

---

### Slide 2: Background & Problem Statement
- **The Core Challenge:** Fluency $\neq$ Factual Correctness.
- **Why Indic & Code-Mixed Text is Difficult:**
  - **Linguistic diversity:** Morphological richness, complex case markers in Hindi.
  - **Code-mixing / Code-switching:** Informal Romanized Hinglish (*"Climate change ki wajah se temperature increase ho raha hai"*).
  - **Extrapolation Risk:** Generative models make ungrounded assumptions when interpreting conversational dialogues.
- **The Three Core Assignment Objectives:**
  1. **Content Preservation:** Retain key facts, entities, numbers, and dates.
  2. **Meaning Preservation:** Accurately convey original semantics across language switches.
  3. **Factual Consistency:** Guarantee every generated claim is strictly supported by source text.

---

### Slide 3: Unified Multilingual Corpus
- **Curated Dataset Pool (500 Candidate Samples):**
  - **150 Hindi News Articles:** Sourced from ILSUM 2.0 (Indian Language Summarization).
  - **150 English News Articles:** Sourced from ILSUM 2.0 Indian national news.
  - **200 Hinglish Dialogues:** Sourced from GupShup (multi-turn code-mixed conversations with English reference summaries).
- **Representative Benchmark Slice:**
  - 18 balanced documents evaluated in-depth (8 Hindi, 5 English, 5 Hinglish).
  - Preprocessed with sentence boundary normalization and clean text tokenization.

---

### Slide 4: The Three Experimental Conditions
- **Condition A (Standard Zero-Shot Prompt):**
  - Generic instruction: *"Provide a concise, comprehensive summary..."*
  - Baseline reflecting typical off-the-shelf LLM behavior without factuality enforcement.
- **Condition B (Factuality-Aware Constrained Prompt):**
  - Explicit negative constraints: strictly prohibit external assumptions, lock down named entities, numbers, and dates; correctly resolve Romanized verbs.
- **Condition C (Automated NLI-Guided Revision Loop):**
  - If Condition B fails automated quality gates, it enters an iterative revision loop ($S_0 \rightarrow S_1 \rightarrow S_2$) guided by an NLI Claim Dependency Graph.

---

### Slide 5: Multi-Stage Factuality Verification Pipeline
```
[Generated Summary] 
        │
        ▼
[1. Atomic Claim Extractor] ──> Deconstructs sentences into factual claims
        │
        ▼
[2. Multilingual Dense Retriever] ──> MiniLM-L12 embeddings find Top-3 source evidence sentences
        │
        ▼
[3. Cross-Lingual NLI Verifier] ──> mDeBERTa-v3 classifies Entailment / Neutral / Contradiction
```
- **Retriever:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-dim dense space).
- **Verifier:** `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` (high-accuracy zero-shot inference).

---

### Slide 6: Automated Acceptance Policy & Formal Definition of $p$
- **Strict Quantitative Decision Gates:**
  1. $\text{Support Rate} \ge 90.0\%$ (at least 90% of extracted propositions must be entailed).
  2. $\text{Contradiction Rate} \le 5.0\%$ (no more than 5% can contradict the source).
  3. **Peak Contradiction Risk Ceiling ($p < 0.70$):**
     $$p \equiv \max_{c_i \in \text{Claims}(S)} P_{\text{NLI}}(\text{contradiction} \mid E_i, c_i) < 0.70$$
     - $P_{\text{NLI}}(\text{contradiction} \mid E_i, c_i)$ is the softmax posterior contradiction probability from `mDeBERTa-v3-base-xnli` given retrieved evidence $E_i$.
     - Enforces that **no individual claim has a contradiction probability $\ge 0.70$** (eliminating silent high-confidence hallucinations).
  4. **Non-Zero Safeguard:** Rejects summaries yielding zero extractable claims (undefined support rate).
- **NetworkX Claim Dependency Graph:**
  - Isolates contradicted subgraphs and dependent clauses, preserving verified entailments during revision.
  - Bounded to $k=2$ attempts: unresolved documents are safely flagged without runaway loops.

---

### Slide 7: Main Benchmark Results (Condition Comparison)

| Metric | Condition A (Standard) | Condition B (Factuality-Aware) | Condition C (Targeted Revision) | Net Delta (C vs. A) |
| :--- | :---: | :---: | :---: | :---: |
| **ROUGE-1 Precision** | 0.3107 | 0.2292 | **0.2104** | -0.1003 |
| **ROUGE-1 Recall** | 0.2844 | 0.2468 | **0.2732** | -0.0112 |
| **ROUGE-1 $F_1$** | 0.2535 | 0.1951 | **0.2126** | -0.0409 |
| **ROUGE-2 $F_1$** | 0.0986 | 0.0583 | **0.0687** | -0.0299 |
| **ROUGE-L $F_1$** | 0.1946 | 0.1477 | **0.1525** | -0.0421 |
| **Macro Factual Support (%)** | 52.50% | 66.11% | **67.99%** | **+15.49%** |
| **Macro Contradiction (%)** | 14.58% | 12.50% | **9.10%** | **-5.48%** |
| **Micro Support (Claims)** | 30/60 (50.0%) | 39/67 (58.21%) | **38/64 (59.38%)** | **+9.38%** |
| **Micro Contradiction (Claims)** | 8/60 (13.33%) | 8/67 (11.94%) | **6/64 (9.38%)** | **-3.95%** |
| **Average Summary Words** | 52.4 words | 59.1 words | 56.0 words | +3.6 words |
| **Compression Ratio (words)** | 27.47% | 27.80% | 27.79% | +0.32% |
| **Inference Latency** | 21.88s | 40.29s | 49.04s | +27.16s |

---

### Slide 8: The Admission Gate vs. Aggregate Cohort Distinction
- **Key Insight:** The Acceptance Policy is an individual summary admission gate, not a corpus average constraint!
- **Disaggregation of Results ($N=18$):**
  - **Accepted Cohort (8 / 18, 44.4%):**
    - **100.0% Support Rate**
    - **0.0% Contradiction Rate**
    - Fully compliant with the strict policy ($	ext{Support} \ge 90\%$, $	ext{Contra} \le 5\%$, $p < 0.70$).
  - **Unresolved Cohort (10 / 18, 55.6%):**
    - 42.4% Support Rate, 16.4% Contradiction Rate.
    - Safely isolated as `UNRESOLVED_FLAGGED` after 2 attempts to protect downstream users.
  - **Full Unfiltered Cohort Mean:** **67.99% Support Rate, 9.10% Contradiction Rate**.
- **Conclusion:** The revision loop elevated overall factuality, but the strict policy was crucial to filter out unresolvable hallucinations.

---

### Slide 9: Claim Evolution & Longitudinal Transitions ($67 \rightarrow 64$)
- **Why did Condition C have 64 claims compared to 67 in Condition B?**
  - **Retained Claims (59 claims):** 13 of 18 documents maintained identical claim counts between B and C.
  - **Pruned Claims (-5 claims):** In verbose Hindi news articles (`ILSUM_HI_006`, `007`, `009`), revision surgically removed 5 ungrounded speculative clauses.
  - **Expanded Grounded Claims (+2 claims):** In `ILSUM_HI_003`, 1 contradicted claim was replaced with 3 fully entailed source-grounded propositions.
  - **Audit Verification:** Documented in `data/claim_transition_audit.csv`—proves that contradiction drops came from targeted factual repair and pruning, not claim extraction drift.

---

### Slide 10: The Hinglish Breakthrough (Code-Mixed Analysis)
- **The Observation:**
  - Condition A standard prompting produced massive hallucinations in Hinglish:
    - **30.0% contradiction rate**
    - **Only 21.3% support rate**
- **The Intervention:**
  - Applying FactIndic's factuality prompt and targeted revision:
    - **Contradiction rate plummeted to 0.0%!**
    - **Support rate jumped to 80.0%!**
- **Takeaway:** Without targeted factuality prompting, LLMs fail on colloquial code-mixing. FactIndic establishes robust cross-lingual stability.

---

### Slide 11: Case Study: Surgical Correction (`ILSUM_HI_003`)
- **Initial Baseline Summary ($S_0$ under Condition B):**
  - Generated an unsupported claim regarding municipal project deadlines.
  - Initial NLI Audit: **100% Contradiction Rate** (0% Support).
- **Targeted Revision Step ($S_1$ under Condition C):**
  - Claim graph isolated the exact faulty proposition.
  - Evidence retriever injected the exact Hindi sentence from the article.
  - Model regenerated the specific clause.
- **Re-Verification Outcome:**
  - Revised claim re-evaluated to **Entailment** ($P > 0.98$).
  - Final Audit: **100% Support Rate, 0% Contradiction Rate** $\rightarrow$ **ACCEPTED**!

---

### Slide 12: Key Scientific Insight: ROUGE vs. Factuality Paradox
- **Why did Condition A have higher ROUGE ($0.2535$ vs $0.2126$) but worse factuality?**
  - High ROUGE does NOT equal truthful summaries!
  - Standard prompts hallucinate popular n-grams that happen to match human reference summaries.
  - Factuality constraints force the model to prune unverified phrases.
  - **Conclusion:** NLI-based factuality verification is an essential complement to surface-level lexical metrics.

---

### Slide 13: System & Engineering Highlights
- **100% Local Inference:** Ran on Apple Silicon MPS (Metal Performance Shaders) using `Qwen2.5-1.5B-Instruct`—zero external API dependencies or costs.
- **Reproducibility:** Fully automated scripts (`generate_summaries_local.py`, `run_verification.py`, `run_revision_pipeline.py`, `evaluate_study.py`).
- **Safety by Design:** Bounded revision attempts ($k=2$), non-zero claim rejection, and zero manual human bottlenecks.

---

### Slide 14: Deliverables Checklist & Summary
- **Deliverables Completed:**
  1. [x] **Source Code & GitHub Repository:** Fully structured and documented.
  2. [x] **Research Paper:** Complete IEEE-style formatted paper in `docs/RESEARCH_PAPER_IEEE.md`.
  3. [x] **Presentation Deck:** Detailed 12-slide defense script in `docs/PRESENTATION_SLIDES.md`.
- **Final Metrics:**
  - Net Factual Support Gain: **+15.49%**
  - Contradiction Reduction: **-5.48%**
  - Hinglish Contradictions: **Eliminated to 0.0%**
- **Thank you! Questions & Discussion.**
