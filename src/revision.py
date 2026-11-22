"""
FactIndic - Phase 5: Targeted Claim-Level Revision Engine
Implements the exact claim-level factuality correction architecture:
1. Preserve Entailed claims (Do not rewrite).
2. For Neutral / Contradicted claims: Correct using only retrieved source evidence.
3. If the topic cannot be verified, return REMOVE (prune the claim).
4. Replace claim in-place in the original summary.
"""

from typing import Dict, Any, List

PROMPT_CLAIM_CORRECTION = """You are a precision claim-level factuality correction system.

Your task is to correct ONE problematic factual claim so that it accurately reflects the provided source evidence.

STRICT RULES:
1. Do not rewrite the entire summary.
2. Do not add background information, assumptions, explanations, or unmentioned context.
3. Do not invent dates, times, locations, people, quantities, or attributions.
4. Strictly preserve who performed the action (Subject) and who received it (Object). Never reverse roles (e.g. if A told B, do NOT say B asked A).
5. If the evidence directly contradicts the claim, correct the claim to state the true fact from the evidence.
6. If the evidence does not establish the claim at all, return REMOVE.
7. Keep the revised claim concise (1 sentence).
8. Do not add introductory phrases such as "According to the source" or "The evidence states".
9. Maintain the language and script of the problematic claim (Hindi in Devanagari, English in English).
10. Return only the corrected claim sentence or REMOVE.

ORIGINAL SOURCE DOCUMENT:
{source}

RETRIEVED EVIDENCE:
{evidence}

PROBLEMATIC CLAIM:
{claim}"""

class TargetedReviser:
    def __init__(self, pipe=None):
        self.pipe = pipe

    def correct_single_claim(self, claim_text: str, evidence_text: str, source_text: str = "") -> str:
        """
        Corrects a single problematic claim using the original source and retrieved evidence.
        Returns the corrected claim string, or 'REMOVE' if it cannot be supported.
        """
        ev = evidence_text.strip() if evidence_text else ""
        src = source_text.strip() if source_text else ev
        if not ev and not src:
            return "REMOVE"

        prompt = PROMPT_CLAIM_CORRECTION.format(
            source=src,
            evidence=ev if ev else src,
            claim=claim_text.strip(),
        )

        if self.pipe is not None:
            messages = [
                {"role": "user", "content": prompt},
            ]
            outputs = self.pipe(
                messages,
                max_new_tokens=80,
                do_sample=False,
                pad_token_id=self.pipe.tokenizer.eos_token_id,
            )
            raw = outputs[0]["generated_text"][-1]["content"].strip()
            cleaned = raw.strip().strip('"').strip("'")
            import re
            cleaned = re.sub(r"^(?:corrected\s+claim|problematic\s+claim|revised\s+claim|correction)\s*:\s*", "", cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r"^(?:सुधारे\s+गए\s+दावे|सुधारा\s+गया\s+दावा|संशोधित\s+दावा)\s*:\s*", "", cleaned, flags=re.IGNORECASE).strip()
            cleaned = cleaned.strip("\"'«»“”")
            if cleaned.upper() == "REMOVE" or cleaned.upper().startswith("REMOVE") or "REMOVE" in cleaned.upper():
                return "REMOVE"
            return cleaned

        return claim_text

    def revise_in_place(self, claim_records: List[Dict[str, Any]], source_text: str = "") -> str:
        """
        Implements the targeted revision architecture:
        - Entailed claims: PRESERVE verbatim (Do not rewrite).
        - Neutral / Contradicted claims: Correct using evidence or prune if REMOVE.
        - Assembles and returns the revised summary string.
        """
        final_sentences = []
        for c in claim_records:
            cid = c.get("claim_id", "")
            text = c.get("claim_text", "").strip()
            label = (c.get("nli_label") or c.get("label") or "").lower()
            evidence = (c.get("retrieved_evidence") or c.get("primary_evidence") or "").strip()

            if label == "entailment":
                # Preserve claim: do not rewrite!
                final_sentences.append(text)
            else:
                # Target revision: Neutral / Contradicted
                corrected = self.correct_single_claim(claim_text=text, evidence_text=evidence, source_text=source_text)
                if corrected and corrected.upper() != "REMOVE":
                    final_sentences.append(corrected)
                else:
                    # Pruned: unsupported claim dropped
                    pass

        if not final_sentences:
            # Fallback if all were removed: keep the first original claim
            return claim_records[0].get("claim_text", "") if claim_records else ""

        return " ".join(final_sentences)

    def revise(
        self,
        source_text: str,
        current_summary: str,
        graph_context: Dict[str, Any] = None,
        claim_records: List[Dict[str, Any]] = None,
    ) -> str:
        """Backward-compatible entry point that delegates to revise_in_place."""
        if claim_records:
            return self.revise_in_place(claim_records)
        return current_summary
