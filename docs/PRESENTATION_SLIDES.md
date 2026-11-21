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

### Slide 6: Automated Acceptance Policy & NetworkX Claim Graph
- **No Manual Human Intervention:** Strict quantitative decision gates:
  1. $\text{Factual Support Rate} \ge 90.0\%$
  2. $\text{Contradiction Rate} \le 5.0\%$
  3. $\text{No High-Confidence Contradictions}$ ($P(\text{contradiction}) < 0.70$)
  4. Non-zero claims requirement (reject empty claims).
- **NetworkX Claim Dependency Graph:**
  - Nodes = Atomic claims; Edges = Shared entities or semantic co-dependencies.
  - When a contradiction occurs, only the affected subgraph is revised, protecting verified entailments from accidental corruption.
- **Bounded Safety:** Capped at $k=2$ revision attempts; lingering ambiguities terminate as `UNRESOLVED_FLAGGED` to eliminate infinite loops.

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

### Slide 8: The Hinglish Breakthrough (Code-Mixed Analysis)
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

### Slide 9: Case Study: Surgical Correction (`ILSUM_HI_003`)
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

### Slide 10: Key Scientific Insight: ROUGE vs. Factuality Paradox
- **Why did Condition A have higher ROUGE ($0.2535$ vs $0.2126$) but worse factuality?**
  - High ROUGE does NOT equal truthful summaries!
  - Standard prompts hallucinate popular n-grams that happen to match human reference summaries.
  - Factuality constraints force the model to prune unverified phrases.
  - **Conclusion:** NLI-based factuality verification is an essential complement to surface-level lexical metrics.

---

### Slide 11: System & Engineering Highlights
- **100% Local Inference:** Ran on Apple Silicon MPS (Metal Performance Shaders) using `Qwen2.5-1.5B-Instruct`—zero external API dependencies or costs.
- **Reproducibility:** Fully automated scripts (`generate_summaries_local.py`, `run_verification.py`, `run_revision_pipeline.py`, `evaluate_study.py`).
- **Safety by Design:** Bounded revision attempts ($k=2$), non-zero claim rejection, and zero manual human bottlenecks.

---

### Slide 12: Deliverables Checklist & Summary
- **Deliverables Completed:**
  1. [x] **Source Code & GitHub Repository:** Fully structured and documented.
  2. [x] **Research Paper:** Complete IEEE-style formatted paper in `docs/RESEARCH_PAPER_IEEE.md`.
  3. [x] **Presentation Deck:** Detailed 12-slide defense script in `docs/PRESENTATION_SLIDES.md`.
- **Final Metrics:**
  - Net Factual Support Gain: **+15.49%**
  - Contradiction Reduction: **-5.48%**
  - Hinglish Contradictions: **Eliminated to 0.0%**
- **Thank you! Questions & Discussion.**
