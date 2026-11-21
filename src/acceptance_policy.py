"""
FactIndic - Phase 5: Acceptance Policy & Decision Engine
Implements the 3 critical acceptance conditions specified in Section 12:
1. Support Rate >= 90%
2. Contradiction Rate <= 5%
3. No high-confidence contradictions (prob_contradiction >= threshold)
Also explicitly handles the edge case where zero claims are extracted (undefined support rate).
"""

from typing import List, Dict, Any, Tuple

DEFAULT_SUPPORT_THRESHOLD = 90.0
DEFAULT_CONTRADICTION_THRESHOLD = 5.0
DEFAULT_HIGH_CONFIDENCE_THRESHOLD = 0.70  # calibrated via validation/inspection

class AcceptancePolicy:
    def __init__(
        self,
        support_threshold: float = DEFAULT_SUPPORT_THRESHOLD,
        contradiction_threshold: float = DEFAULT_CONTRADICTION_THRESHOLD,
        high_confidence_threshold: float = DEFAULT_HIGH_CONFIDENCE_THRESHOLD,
    ):
        self.support_threshold = support_threshold
        self.contradiction_threshold = contradiction_threshold
        self.high_confidence_threshold = high_confidence_threshold

    def evaluate(self, claim_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates a verified summary against acceptance policy.
        Returns:
            {
                "accepted": bool,
                "status": "ACCEPTED" | "REVISE_LOW_SUPPORT" | "REVISE_CONTRADICTION" | "REVISE_ZERO_CLAIMS",
                "support_rate": float,
                "contradiction_rate": float,
                "neutral_rate": float,
                "high_confidence_contradictions": List[Dict],
                "flagged_claims": List[Dict],
                "reasons": List[str],
            }
        """
        total_claims = len(claim_records)

        # Implementation Decision 2: Handle Zero Claims
        if total_claims == 0:
            return {
                "accepted": False,
                "status": "REVISE_ZERO_CLAIMS",
                "support_rate": 0.0,
                "contradiction_rate": 0.0,
                "neutral_rate": 0.0,
                "high_confidence_contradictions": [],
                "flagged_claims": [],
                "reasons": ["Zero claims extracted; support rate is undefined. Summary rejected."],
            }

        entailments = [c for c in claim_records if c["nli_label"] == "entailment"]
        contradictions = [c for c in claim_records if c["nli_label"] == "contradiction"]
        neutrals = [c for c in claim_records if c["nli_label"] == "neutral"]

        support_rate = round((len(entailments) / total_claims) * 100, 2)
        contradiction_rate = round((len(contradictions) / total_claims) * 100, 2)
        neutral_rate = round((len(neutrals) / total_claims) * 100, 2)

        # Implementation Decision 1: High-Confidence Contradictions
        high_conf_contradictions = [
            c for c in claim_records
            if c.get("prob_contradiction", 0.0) >= self.high_confidence_threshold
        ]

        # Flagged claims needing revision (contradictions + unestablished neutrals)
        flagged_claims = [c for c in claim_records if c["nli_label"] in ["contradiction", "neutral"]]

        reasons = []
        is_accepted = True

        # Condition 1: Support Rate >= 90%
        if support_rate < self.support_threshold:
            is_accepted = False
            reasons.append(f"Support Rate ({support_rate}%) is below threshold ({self.support_threshold}%).")

        # Condition 2: Contradiction Rate <= 5%
        if contradiction_rate > self.contradiction_threshold:
            is_accepted = False
            reasons.append(f"Contradiction Rate ({contradiction_rate}%) exceeds threshold ({self.contradiction_threshold}%).")

        # Condition 3: No High-Confidence Contradictions
        if len(high_conf_contradictions) > 0:
            is_accepted = False
            reasons.append(
                f"Found {len(high_conf_contradictions)} high-confidence contradiction(s) "
                f"(confidence >= {self.high_confidence_threshold})."
            )

        status = "ACCEPTED" if is_accepted else "REVISE_FLAGGED"
        if not is_accepted and len(high_conf_contradictions) > 0:
            status = "REVISE_HIGH_CONF_CONTRADICTION"

        return {
            "accepted": is_accepted,
            "status": status,
            "support_rate": support_rate,
            "contradiction_rate": contradiction_rate,
            "neutral_rate": neutral_rate,
            "total_claims": total_claims,
            "high_confidence_contradictions": high_conf_contradictions,
            "flagged_claims": flagged_claims,
            "reasons": reasons if reasons else ["Satisfies all 3 acceptance criteria."],
        }
