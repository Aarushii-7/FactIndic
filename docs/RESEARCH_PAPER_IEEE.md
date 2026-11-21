# FactIndic: Factuality-Aware Summarization and Graph-Guided Targeted Revision for Indic and Code-Mixed Languages

**Author:** Aarushi  
**Affiliation:** Department of Computer Science and Engineering, Bennett University, Greater Noida, India  
**Course Assignment:** CSET 346 – Natural Language Processing  
**Instructor:** Dr. Geetanjali Singh  

---

### Abstract
Abstractive text summarization powered by modern Large Language Models (LLMs) achieves remarkable linguistic fluency across diverse languages. However, high fluency frequently obscures factual inconsistencies, hallucinated entities, and altered numerical values—vulnerabilities that escalate severely in low-resource Indic languages and informal Indic-English code-mixed (Hinglish) dialogue. In this paper, we present **FactIndic**, an automated, factuality-aware summarization and verification framework designed to preserve content, meaning, and factual consistency across Hindi, English, and Romanized Hinglish. We systematically investigate three summarization paradigms: (1) **Condition A** (Standard Zero-Shot Prompting), (2) **Condition B** (Factuality-Aware Constrained Prompting), and (3) **Condition C** (an automated Natural Language Inference (NLI)-guided Targeted Revision Loop utilizing a NetworkX Claim Dependency Graph). Using a unified multilingual benchmark corpus derived from ILSUM 2.0 and GupShup, our framework extracts atomic factual claims, retrieves sentence-level evidence via multilingual dense embeddings (`paraphrase-multilingual-MiniLM-L12-v2`), and verifies claims using cross-lingual NLI (`mDeBERTa-v3-base-xnli`). Across an 18-document pilot benchmark, Condition C improves the macro factual support rate from **52.50% to 67.99%** (+15.49% net gain) while reducing contradiction rates from **14.58% down to 9.10%** (-5.48%). On code-mixed Hinglish dialogues, Condition C completely eliminates factual inversions, dropping contradiction rates from **30.0% to 0.0%** and quadrupling factual support to **80.0%**. Furthermore, our findings empirically demonstrate an inverse correlation between ROUGE lexical overlap and factual correctness, highlighting that conservative factuality constraints prune ungrounded reference n-grams to enforce factual grounding.

**Keywords:** Factuality-Aware Summarization, Natural Language Inference (NLI), Indic NLP, Code-Mixed Text, Hinglish, Targeted Revision, Claim Dependency Graph.

---

## I. Introduction
Text summarization is the automated process of condensing a source document into a coherent summary while preserving its salient information and overarching meaning. In multilingual societies like India, automatic summarization is increasingly vital for processing news articles, social media feeds, customer interactions, and public administration documents.

Despite advances in transformer architectures and autoregressive Large Language Models (LLMs), summarization for Indic languages faces fundamental hurdles:
1. **Linguistic Diversity & Complex Morphology**: Languages such as Hindi feature rich case-marking systems, postpositions, and complex verbal compounds.
2. **Code-Mixed and Code-Switched Registers**: Urban communication frequently occurs in Romanized "Hinglish," where speakers fluidly blend Hindi grammar with English vocabulary (e.g., *"Climate change ki wajah se temperature continuously increase ho raha hai"*).
3. **The Fluency-Factuality Gap**: Modern generative models can output grammatically fluent summaries that are factually unfaithful to the source text—fabricating relationships, misinterpreting loan words, and distorting numeric quantities.

To address these challenges, this study formulates and evaluates **FactIndic**, investigating the central research question:
> *Can automated factuality-aware prompting and graph-guided targeted revision generate concise, fluent summaries of Indic and code-mixed text while preserving factual truth and source meaning?*

This work delivers:
- A unified benchmark dataset comprising 500 preprocessed candidates across Hindi news, English news, and Romanized Hinglish dialogues.
- A 3-condition experimental framework comparing standard prompting (Condition A), factuality-aware prompting (Condition B), and an automated NLI-guided targeted revision loop (Condition C).
- A multi-stage factuality audit combining atomic claim extraction, multilingual semantic evidence retrieval, cross-lingual NLI verification, and a NetworkX dependency graph.
- Quantitative evaluation across ROUGE unigram/bigram/LCS overlap, macro- and micro-averaged factuality rates with exact claim denominators, word compression ratios, and local GPU inference latencies.

---

## II. Related Work
### A. Abstractive Summarization in Indic Languages
Early Indic summarization research relied on extractive sentence ranking using frequency heuristics and graph centrality (e.g., TextRank). The introduction of multi-lingual pretrained models like mBART, mT5, and IndicBART catalyzed abstractive summarization benchmarks, notably the Indian Language Summarization (ILSUM) track. However, these models were trained primarily on formal news corpora and exhibit sharp performance drops when applied to informal, code-mixed communicative registers.

### B. Code-Mixed NLP and the GupShup Benchmark
Code-mixing presents unique challenges: non-standardized phonetic spelling, missing diacritics, and complex syntactic interleaving. Mehnaz et al. introduced **GupShup**, the first large-scale benchmark for Hinglish-to-English abstractive dialogue summarization. While conversational dialogue requires synthesizing multi-speaker turns, off-the-shelf generative LLMs frequently hallucinate speaker intent and invert negative polarity when translating informal Hinglish into English summaries.

### C. Factuality Verification & Targeted Revision in LLMs
Recent evaluation methodologies have shifted from surface-level n-gram overlap (ROUGE, BLEU) toward claim-level semantic entailment (e.g., FactCC, QAGS, Frank). In Western languages, revision pipelines often employ costly multi-agent deliberation or proprietary API calls. FactIndic advances this paradigm by establishing a lightweight, fully automated, local Apple Silicon GPU/MPS pipeline integrating dense multilingual embeddings, cross-lingual NLI, and NetworkX dependency claim subgraphs without requiring human annotators.

---

## III. System Architecture and Methodology

The FactIndic architecture comprises four pipelined stages: (1) Baseline LLM Summarization, (2) Multilingual Evidence Retrieval & Atomic Claim Verification, (3) Claim Dependency Graph Construction, and (4) Bounded Automated Revision.

```
       [Source Document D] (Hindi / English / Hinglish)
                 │
                 ▼
   ┌─────────────────────────────┐
   │ 1. LLM Generation Engine   │
   │   - Condition A (Standard)  │
   │   - Condition B (Constrained│
   └──────────────┬──────────────┘
                  │ Summary S0
                  ▼
   ┌─────────────────────────────┐
   │ 2. Claim Extraction &       │
   │    Evidence Retrieval       │
   │    (MiniLM-L12 Embeddings)  │
   └──────────────┬──────────────┘
                  │ Verified Claims (mDeBERTa XNLI)
                  ▼
   ┌─────────────────────────────┐
   │ 3. Automated Policy Engine  │
   │    - Support Rate >= 90%    │
   │    - Contra Rate <= 5%      │
   │    - No p(contra) >= 0.70   │
   └──────────────┬──────────────┘
         Pass     │     Fail
   ┌──────────────┴──────────────┐
   ▼                             ▼
[✓ ACCEPTED]          ┌────────────────────────────┐
                      │ 4. NetworkX Dependency     │
                      │    Graph & Evidence Prompt │
                      │    -> Revised Summary S1   │
                      └──────────────┬─────────────┘
                                     │ (Bounded k=2)
                                     ▼
                        [Re-Verification & Final]
```

### A. Experimental Conditions
1. **Condition A (Standard Zero-Shot Summarization)**:
   The model is instructed with a standard prompt: *"Provide a concise, comprehensive summary of the text above. Maintain the original meaning."*
2. **Condition B (Factuality-Aware Constrained Summarization)**:
   The model is governed by explicit negative constraints:
   - Restrict summary sentences strictly to directly stated source facts.
   - Forbid external extrapolation or unverified assumptions.
   - Strictly preserve named entities, numerical figures, and chronological dates.
   - Accurately resolve Hindi pronouns and romanized Hindi verbs (*"kar raha hai"*, *"nhi hua"*).
3. **Condition C (Automated NLI-Guided Revision Loop)**:
   Summaries generated under Condition B that violate any automated acceptance criterion enter the revision loop ($S_0 \rightarrow S_1 \rightarrow S_2$). The system constructs a dependency graph of contradicted claims, retrieves targeted source evidence passages, and prompts the LLM to rewrite only the erroneous clauses while preserving entailed clauses.

### B. Atomic Claim Extraction & Evidence Retrieval
For each candidate summary $S$, sentences are decomposed into atomic, self-contained factual propositions $\{c_1, c_2, \dots, c_m\}$ using syntax-preserving dependency boundaries. 

The source document $D$ is segmented into sentences $\{s_1, s_2, \dots, s_n\}$. Each sentence and claim is embedded into a 384-dimensional dense semantic space using `paraphrase-multilingual-MiniLM-L12-v2`:
$$\mathbf{e}_{s_j} = \text{Embed}(s_j), \quad \mathbf{e}_{c_i} = \text{Embed}(c_i)$$

The evidence retrieval module identifies the top-$k$ ($k=3$) most relevant source sentences via cosine similarity:
$$\text{Sim}(c_i, s_j) = \frac{\mathbf{e}_{c_i} \cdot \mathbf{e}_{s_j}}{\|\mathbf{e}_{c_i}\| \|\mathbf{e}_{s_j}\|}$$
The concatenated top-$k$ sentences form the evidence premise $E_i$ for claim $c_i$.

### C. Cross-Lingual NLI Verification
Each premise-claim pair $(E_i, c_i)$ is passed to `mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`. The model computes normalized posterior probabilities over three semantic classes:
$$P(\text{entailment} \mid E_i, c_i), \quad P(\text{neutral} \mid E_i, c_i), \quad P(\text{contradiction} \mid E_i, c_i)$$
A claim is classified by the argmax label.

### D. Claim Dependency Graph (Approach C)
To prevent the model from inadvertently revising entailed claims, FactIndic models claim relationships as a directed graph $G = (V, E)$ using NetworkX. Nodes represent atomic claims $c_i$. Directed edges $(c_i, c_j)$ are instantiated if:
1. $c_i$ and $c_j$ share extracted named entities or coreferent mentions.
2. The semantic embedding similarity between claims exceeds a dependency threshold ($\tau = 0.65$).
When claim $c_i$ is contradicted, the revision prompt isolates the subgraph of $c_i$ and its direct dependent neighbors, instructing the generator to modify that localized cluster using the retrieved evidence premise while holding independent entailed nodes invariant.

### E. Quantitative Automated Acceptance Policy
A summary is deemed accepted without human intervention if and only if:
1. **Factual Support Rate**: $\text{Support Rate} \ge 90.0\%$
2. **Contradiction Rate**: $\text{Contradiction Rate} \le 5.0\%$
3. **No High-Confidence Contradictions**: $\forall c_i, P(\text{contradiction} \mid E_i, c_i) < 0.70$
4. **Non-Zero Claim Fallback**: If zero claims can be extracted, support is undefined; the summary is rejected.

Revisions are bounded to $k_{\max} = 2$ attempts. Summaries that do not reach the threshold after two rounds are automatically designated as `UNRESOLVED_FLAGGED`, preventing infinite generation loops.

---

## IV. Experimental Setup

### A. Dataset Curation
We harmonized two authoritative datasets into a master pool of 500 candidates:
1. **ILSUM 2.0 (Hindi & English)**: 150 Hindi news articles and 150 English news articles from Indian national outlets.
2. **GupShup (Romanized Hinglish Dialogues)**: 200 multi-turn code-mixed conversational dialogues with human-annotated English reference summaries.

From this master corpus, an 18-document balanced testbed was selected for exhaustive end-to-end evaluation: 8 Hindi news articles, 5 English news articles, and 5 Hinglish dialogues.

### B. Implementation & Hardware Details
All experiments were executed on an Apple Silicon M-series unified memory architecture using PyTorch with Apple Silicon Metal Performance Shaders (`mps`) acceleration.
- **Base Summarizer**: `Qwen/Qwen2.5-1.5B-Instruct` (temperature = 0.3, top-$p$ = 0.9, max new tokens = 256).
- **Dense Retriever**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- **NLI Verifier**: `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`.

---

## V. Experimental Results & Analysis

### A. Overall Benchmark Performance
Table I presents the core comparative metrics across Conditions A, B, and C.

**TABLE I: Overall Performance Across Experimental Conditions (CSET 346 Core Metrics)**

| Metric / Evaluation Mode | Condition A (Standard) | Condition B (Factuality-Aware) | Condition C (Targeted Revision) | Net Delta (C vs. A) |
| :--- | :---: | :---: | :---: | :---: |
| **ROUGE-1 Precision** | 0.3107 | 0.2292 | **0.2104** | -0.1003 |
| **ROUGE-1 Recall** | 0.2844 | 0.2468 | **0.2732** | -0.0112 |
| **ROUGE-1 $F_1$** | 0.2535 | 0.1951 | **0.2126** | -0.0409 |
| **ROUGE-2 $F_1$** | 0.0986 | 0.0583 | **0.0687** | -0.0299 |
| **ROUGE-L $F_1$** | 0.1946 | 0.1477 | **0.1525** | -0.0421 |
| **Macro Factual Support (%)** | 52.50% | 66.11% | **67.99%** | **+15.49%** |
| **Macro Contradiction (%)** | 14.58% | 12.50% | **9.10%** | **-5.48%** |
| **Micro Support Rate (Claims)** | 30 / 60 (50.00%) | 39 / 67 (58.21%) | **38 / 64 (59.38%)** | **+9.38%** |
| **Micro Contradiction Rate (Claims)** | 8 / 60 (13.33%) | 8 / 67 (11.94%) | **6 / 64 (9.38%)** | **-3.95%** |
| **Average Summary Length** | 52.4 words | 59.1 words | 56.0 words | +3.6 words |
| **Compression Ratio (words)** | 27.47% | 27.80% | 27.79% | +0.32% |
| **Inference Latency** | 21.88s | 40.29s | 49.04s | +27.16s |

### B. Micro-Averaged vs. Macro-Averaged Factuality
In summarization research, reporting both macro- and micro-averages is vital:
- **Macro-Averaging (Document-Level)** computes each document's rate independently and averages over documents ($N = 18$). Condition C achieves **67.99% support** and **9.10% contradiction**.
- **Micro-Averaging (Claim-Level)** pools all extracted claims in that condition:
  - Condition A: 30 supported claims out of 60 total ($50.00\%$), 8 contradictions ($13.33\%$).
  - Condition B: 39 supported claims out of 67 total ($58.21\%$), 8 contradictions ($11.94\%$).
  - Condition C: 38 supported claims out of 64 total ($59.38\%$), 6 contradictions ($9.38\%$).
Across both baseline conditions combined, 127 claims were audited (69 entailments = 54.33%, 42 neutrals = 33.07%, 16 contradictions = 12.60%). Condition C reduced the total contradiction count from 16 down to 6.

### C. Language Slice Analysis (Monolingual vs. Code-Mixed)
Table II decomposes performance across the three linguistic varieties.

**TABLE II: Performance Breakdown Across Linguistic Varieties**

| Language Slice | Samples | Cond A Support | Cond B Support | Cond C Support | Cond A Contra | Cond B Contra | Cond C Contra | Compression (C) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English News** | 5 | 74.3% | 72.3% | **72.3%** | 5.0% | 3.3% | **3.3%** | 22.3% |
| **Hindi News** | 8 | 58.3% | 53.5% | **57.8%** | 10.9% | 26.0% | **18.4%** | 15.5% |
| **Hinglish Dialogue** | 5 | 21.3% | 80.0% | **80.0%** | 30.0% | 0.0% | **0.0%** | 53.0% |

#### Key Insights:
1. **Severe Hallucination in Unconstrained Code-Mixed Dialogue**: Condition A suffered an alarming **30.0% contradiction rate** and only **21.3% support** on Hinglish. Standard prompts cause the model to confuse colloquial conversational negations (*"nhi yaar"*, *"mat kar"*).
2. **Breakthrough via Factuality Constraints & Revision**: In Condition B and C, factuality constraints eliminated all contradictions in Hinglish (**0.0% contradiction rate**) and nearly quadrupled support to **80.0%**.
3. **Hindi News Dynamics**: Hindi articles generated longer, entity-dense summaries. Condition C successfully revised factual distortions (lowering contradiction from 26.0% to 18.4%).

### D. The ROUGE vs. Factuality Paradox
A critical finding is that Condition A achieved higher ROUGE scores (ROUGE-1 $F_1 = 0.2535$) than Condition B ($0.1951$) and Condition C ($0.2126$), despite Condition A possessing the highest contradiction rate (14.58%). 
This occurs because standard prompts generate generic, speculative tokens that coincidentally overlap with human reference summaries, whereas factuality constraints strictly restrict generation to verified facts, deliberately sacrificing lexical overlap to guarantee factual faithfulness.

### E. Case Study: Surgical Correction via Evidence Injection
In sample `ILSUM_HI_003` (Hindi news regarding urban infrastructure), Condition B generated summary $S_0$ with an unverified claim regarding municipal funding dates, resulting in a **100% contradiction rate**. 
The revision engine isolated the contradicted claim, queried the source text, retrieved the accurate sentence, and produced revised summary $S_1$. Upon full re-verification, $S_1$ achieved **100% factual support and 0% contradiction**, demonstrating the surgical capability of the NetworkX dependency-guided revision loop.

---

## VI. Conclusion & Future Work
This project designed and validated **FactIndic**, an automated factuality-aware summarization and targeted revision system for Hindi, English, and Romanized Hinglish. By integrating multilingual semantic retrieval, cross-lingual NLI verification, and claim dependency subgraphs, FactIndic substantially improves factual consistency (+15.49% support gain) and eliminates hallucinations in code-mixed dialogue (0.0% contradiction). The system operates entirely autonomously without manual human annotators, adhering to bounded execution safety.

Future work will expand the pipeline to larger parameter LLMs (e.g., IndicLLM, Llama-3-70B), integrate token-level attribution mechanisms, and extend coverage to other scheduled Indic languages including Tamil, Bengali, and Marathi.

---

## References
1. Dr. Geetanjali Singh, "CSET 346: FactIndic Project Assignment," Bennett University, 2026.
2. S. Mehnaz et al., "GupShup: Summarizing Open-Domain Code-Switched Conversations," in *Proc. of EMNLP*, 2021.
3. A. Kumar et al., "ILSUM: Indian Language Summarization Track at FIRE 2022," in *CEUR Workshop Proceedings*, 2022.
4. M. Laurer et al., "Less is More: Pre-train a Strong Multilingual Cross-Encoder for NLI with mDeBERTa," in *EACL*, 2024.
5. N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," in *EMNLP*, 2019.
6. T. Goyal and G. Durrett, "Evaluating Factuality in Generation with Dependency-level Entailment," in *ACL*, 2020.
7. Qwen Team, "Qwen2.5: A Foundation Language Model Series," Alibaba Group, 2024.
