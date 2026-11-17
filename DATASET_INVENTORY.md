# FactIndic – Dataset Inventory

## 1. ILSUM 2.0 – Hindi
- Language: Hindi
- Dataset: ILSUM 2.0
- Selected samples: 150
- Split: Train
- File: `data/ilsum/hindi_150_candidates.csv`
- Fields: `id`, `Heading`, `Summary`, `Article`
- Status: Downloaded, inspected, filtered and sampled

## 2. ILSUM 2.0 – English
- Language: English
- Dataset: ILSUM 2.0
- Selected samples: 150
- Split: Train
- File: `data/ilsum/english_150_candidates.csv`
- Fields: `id`, `Heading`, `Summary`, `Article`
- Status: Downloaded, inspected, filtered and sampled

## 3. GupShup – Hinglish to English
- Language: Romanized Hindi-English (Hinglish)
- Dataset: GupShup
- Selected samples: 200
- Split: Validation
- File: `data/gupshup/gupshup_200_validation_candidates.csv`
- Fields: `sample_id`, `original_index`, `split`, `source_text`, `reference_summary`
- Status: Downloaded, inspected, sampled, stripped of trailing newlines, and verified

## 4. GupShup – Test
- Language: Hinglish to English
- Available pairs: 500
- Files: `data/gupshup/test.source`, `data/gupshup/test.target`
- Status: Inspected; reserved for final evaluation

## 5. GupShup – Training Data Limitation
- `train.target` is available with 5,831 lines.
- `train.source` is missing.
- Complete training source-summary pairs are therefore unavailable.
- Note: This does not affect zero-shot / few-shot LLM summarization and NLI verification on validation/test candidates.

## 6. Unified Evaluation Master Set (FactIndic Guide Architecture)
- File: `data/candidates_master.csv`
- Total samples: 500
  - Hindi (ILSUM): 150
  - English (ILSUM): 150
  - Hinglish (GupShup): 200
- Schema:
  - `sample_id`: Unique identifier (`ILSUM_HI_001`–`150`, `ILSUM_EN_001`–`150`, `GUP_001`–`200`)
  - `original_id`: Identifier in upstream dataset
  - `dataset`: Upstream source (`ILSUM` or `GupShup`)
  - `language`: `hindi`, `english`, or `hinglish`
  - `language_type`: `monolingual_indic`, `monolingual_english`, or `code_mixed`
  - `genre`: `news` or `dialogue`
  - `heading`: News headline (if available)
  - `source_text`: Standardized, stripped source text
  - `reference_summary`: Standardized, stripped reference summary
- Status: Ready for Phase 3 (LLM Summarization Baseline) and Phase 4 (Verification Pipeline).
