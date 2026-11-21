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
        Runs NLI inference on (premise, hypothesis).
        Returns:
            {
                "label": "entailment" | "contradiction" | "neutral",
                "confidence": float,
                "probabilities": {"entailment": p1, "neutral": p2, "contradiction": p3}
            }
        """
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

        # Predict top class
        best_label = max(prob_dict, key=prob_dict.get)
        confidence = prob_dict[best_label]

        return {
            "label": best_label,
            "confidence": confidence,
            "probabilities": prob_dict,
        }
