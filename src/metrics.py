"""
FactIndic - Phase 6: Evaluation Metrics Engine
Implements Section 13 & 14 metrics:
- ROUGE-1, ROUGE-2, ROUGE-L (lexical overlap with reference summaries)
- Compression Ratio (%) based on word count and character count
- Content length and statistics
"""

import re
from collections import Counter
from typing import Dict, Any, List, Tuple

def tokenize(text: str) -> List[str]:
    """Tokenizes text into words across English, Indic scripts, and numbers."""
    if not text or not isinstance(text, str):
        return []
    return re.findall(r"\b[\w\u0900-\u097F]+\b", text.lower())

def compute_ngram_f1(ref_tokens: List[str], gen_tokens: List[str], n: int = 1) -> Tuple[float, float, float]:
    """Computes precision, recall, and F1 for n-grams."""
    if len(ref_tokens) < n or len(gen_tokens) < n:
        return 0.0, 0.0, 0.0

    ref_ngrams = Counter([tuple(ref_tokens[i:i+n]) for i in range(len(ref_tokens)-n+1)])
    gen_ngrams = Counter([tuple(gen_tokens[i:i+n]) for i in range(len(gen_tokens)-n+1)])

    overlap = sum((ref_ngrams & gen_ngrams).values())
    rec = overlap / sum(ref_ngrams.values()) if ref_ngrams else 0.0
    prec = overlap / sum(gen_ngrams.values()) if gen_ngrams else 0.0
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

    return round(prec, 4), round(rec, 4), round(f1, 4)

def compute_lcs(seq1: List[str], seq2: List[str]) -> int:
    """Computes length of longest common subsequence between two token lists."""
    m, n = len(seq1), len(seq2)
    dp = [0] * (n + 1)
    for i in range(1, m + 1):
        prev = 0
        for j in range(1, n + 1):
            temp = dp[j]
            if seq1[i - 1] == seq2[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = temp
    return dp[n]

def compute_rouge_l(ref_tokens: List[str], gen_tokens: List[str]) -> Tuple[float, float, float]:
    """Computes ROUGE-L precision, recall, and F1."""
    if not ref_tokens or not gen_tokens:
        return 0.0, 0.0, 0.0

    lcs_len = compute_lcs(ref_tokens, gen_tokens)
    rec = lcs_len / len(ref_tokens)
    prec = lcs_len / len(gen_tokens)
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

    return round(prec, 4), round(rec, 4), round(f1, 4)

def evaluate_summary_lexical(reference_text: str, generated_text: str) -> Dict[str, float]:
    """Computes ROUGE-1, ROUGE-2, and ROUGE-L metrics."""
    ref_tok = tokenize(reference_text)
    gen_tok = tokenize(generated_text)

    p1, r1, f1 = compute_ngram_f1(ref_tok, gen_tok, n=1)
    p2, r2, f2 = compute_ngram_f1(ref_tok, gen_tok, n=2)
    pl, rl, fl = compute_rouge_l(ref_tok, gen_tok)

    return {
        "rouge1_f1": f1,
        "rouge1_p": p1,
        "rouge1_r": r1,
        "rouge2_f1": f2,
        "rouge2_p": p2,
        "rouge2_r": r2,
        "rougeL_f1": fl,
        "rougeL_p": pl,
        "rougeL_r": rl,
    }

def compute_compression_ratio(source_text: str, summary_text: str) -> Dict[str, Any]:
    """
    Computes compression ratio: (summary_len / source_len) * 100
    State length in both words and characters.
    """
    source_words = len(tokenize(source_text))
    summary_words = len(tokenize(summary_text))
    source_chars = len(str(source_text).strip())
    summary_chars = len(str(summary_text).strip())

    word_ratio = round((summary_words / source_words) * 100, 2) if source_words > 0 else 0.0
    char_ratio = round((summary_chars / source_chars) * 100, 2) if source_chars > 0 else 0.0

    return {
        "source_words": source_words,
        "summary_words": summary_words,
        "source_chars": source_chars,
        "summary_chars": summary_chars,
        "compression_ratio_words": word_ratio,
        "compression_ratio_chars": char_ratio,
    }
