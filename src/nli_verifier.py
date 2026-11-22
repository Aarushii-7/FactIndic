"""
FactIndic - Phase 4: Multilingual Natural Language Inference (NLI) Verifier
Compares retrieved source evidence (premise) against an atomic claim (hypothesis).
Predicts whether the claim is:
  - ENTAILMENT (Supported by source)
  - CONTRADICTION (Refuted / contradicts source)
  - NEUTRAL (Not established / outside knowledge)
"""

from typing import Dict, Any
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class NLIVerifier:
    def __init__(
        self,
        model_name: str = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
        device: str = None,
    ):
        if device is None:
            self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        else:
            self.device = device

        print(f"Loading NLI Model ({model_name}) on {self.device}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
        except Exception:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        try:
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True)
        except Exception:
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        try:
            self.model.to(torch.device(self.device))
        except Exception:
            self.device = "cpu"
            self.model.to(torch.device("cpu"))
        self.model.eval()

        # Map labels to lowercase standard: entailment, neutral, contradiction
        self.id2label = {
            k: v.lower() for k, v in self.model.config.id2label.items()
        }
        print(f"NLI Model ready! Labels: {self.id2label}")

    def verify(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        Runs NLI inference on (premise, hypothesis) using calibrated decision thresholds.
        Returns:
            {
                "label": "entailment" | "contradiction" | "neutral",
                "confidence": float,
                "probabilities": {"entailment": p1, "neutral": p2, "contradiction": p3}
            }
        """
        premise = str(premise).strip()
        hypothesis = str(hypothesis).strip()

        # Handle empty/missing premise safely
        if not premise or not hypothesis:
            return {
                "label": "neutral",
                "confidence": 1.0,
                "probabilities": {"entailment": 0.0, "neutral": 1.0, "contradiction": 0.0},
            }

        inputs = self.tokenizer(
            premise,
            hypothesis,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        ).to(torch.device(self.device))

        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)[0].cpu().tolist()

        prob_dict = {
            self.id2label[i]: round(probs[i], 4)
            for i in range(len(probs))
        }

        p_ent = prob_dict.get("entailment", 0.0)
        p_neu = prob_dict.get("neutral", 0.0)
        p_con = prob_dict.get("contradiction", 0.0)

        # Calibrated decision rules:
        # 1. Contradiction: If contradiction is prominent or exceeds entailment
        if p_con >= 0.45 or (p_con > p_ent and p_con >= 0.35):
            best_label = "contradiction"
            confidence = p_con
        # 2. Strict Entailment: requires robust confidence without substantial neutral uncertainty
        elif p_ent >= 0.65 and p_ent > p_neu + 0.10:
            best_label = "entailment"
            confidence = p_ent
        # 3. Neutral: Evidence is insufficient or does not firmly establish the claim
        else:
            best_label = "neutral"
            confidence = p_neu if p_neu >= p_ent else round(1.0 - p_ent, 4)

        return {
            "label": best_label,
            "confidence": confidence,
            "probabilities": prob_dict,
        }
