"""
FactIndic - Phase 4: Atomic Claim Extractor
Decomposes a generated summary into atomic, checkable factual claims (C1, C2, ...).
Preserves numbers, names, dates, actions, and relationships.
"""

import re
import json
from typing import List, Dict, Any

PROMPT_CLAIM_EXTRACTION = """Decompose the following summary into atomic, checkable factual claims.
Each claim must express exactly ONE fact (an entity, number, date, action, cause, or relation).
Do not combine multiple facts with "and".
Output ONLY a valid JSON list of strings, for example:
["Claim 1", "Claim 2", "Claim 3"]

Summary:
{summary}

JSON:"""

def rule_based_claim_split(text: str) -> List[str]:
    """Fallback: splits summary on sentences and major clauses if LLM JSON parsing fails."""
    # Split on sentence boundaries and bullet points
    raw = re.split(r"(?<=[.!?।\n])\s+|(?<=\*)\s+", text)
    cleaned = []
    for s in raw:
        s = re.sub(r"^[\s\*\-\d\.\)]+", "", s).strip()
        if len(s) > 10:
            cleaned.append(s)
    return cleaned if cleaned else [text.strip()]

class ClaimExtractor:
    def __init__(self, pipe=None):
        """
        Takes an optional text-generation pipeline (e.g. Qwen).
        If pipe is None, uses sentence-level splitting.
        """
        self.pipe = pipe

    def extract_claims(self, summary_text: str) -> List[Dict[str, str]]:
        """
        Extracts atomic claims from summary_text.
        Returns: [{"claim_id": "C1", "claim_text": "..."}, ...]
        """
        summary_text = str(summary_text).strip()
        if not summary_text:
            return []

        claims_raw = []

        if self.pipe is not None:
            prompt = PROMPT_CLAIM_EXTRACTION.format(summary=summary_text)
            messages = [
                {"role": "system", "content": "You are a precise factual claim extractor. Output ONLY a valid JSON array of strings."},
                {"role": "user", "content": prompt}
            ]
            try:
                outputs = self.pipe(
                    messages,
                    max_new_tokens=250,
                    temperature=0.1,
                    do_sample=False,
                    pad_token_id=self.pipe.tokenizer.eos_token_id,
                )
                content = outputs[0]["generated_text"][-1]["content"].strip()

                # Extract JSON array using regex if surrounded by markdown
                match = re.search(r"\[.*\]", content, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
                        claims_raw = [x.strip() for x in parsed if len(x.strip()) > 5]
            except Exception as e:
                # LLM parse fallback
                pass

        # Fallback if LLM extraction returned empty
        if not claims_raw:
            claims_raw = rule_based_claim_split(summary_text)

        # Structure with IDs
        structured = [
            {"claim_id": f"C{i}", "claim_text": c}
            for i, c in enumerate(claims_raw, start=1)
        ]
        return structured
