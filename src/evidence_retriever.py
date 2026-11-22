"""
FactIndic - Phase 4: Multilingual Evidence Retriever
Splits source text into sentences or dialogue turns, computes multilingual embeddings,
and retrieves top-k relevant candidate evidence units for each atomic claim.
"""

import re
from typing import List, Dict, Any
import numpy as np
import torch

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    SentenceTransformer = None

def split_source_into_units(text: str, genre: str = "news") -> List[str]:
    """
    Splits text into checkable evidence sentences or conversational turns.
    - News: splits on Devanagari danda (।), period (.), exclamation, question mark, newline.
    - Dialogue: splits on speaker turns (e.g. 'Speaker: utterance') or lines.
    """
    text = str(text).strip()
    if not text:
        return []

    if genre == "dialogue":
        # 1. Try splitting on newline
        lines = [line.strip() for line in re.split(r"[\r\n]+", text) if len(line.strip()) > 3]
        if len(lines) > 1:
            return lines
        # 2. Try splitting on speaker patterns (e.g. 'Amanda:', 'Jerry:')
        parts = re.split(r"(?=[A-Za-z0-9_-]+:)", text)
        cleaned = [p.strip() for p in parts if len(p.strip()) > 3]
        if len(cleaned) > 1:
            return cleaned
        return [text]
    else:
        # News article: split by danda, full stops, question marks, newlines
        parts = re.split(r"(?<=[।!?.\n])\s+", text)
        cleaned = [p.strip() for p in parts if len(p.strip()) > 8]
        return cleaned if cleaned else [text]

class EvidenceRetriever:
    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        device: str = None,
    ):
        if device is None:
            self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        else:
            self.device = device

        print(f"Loading Evidence Retriever ({model_name}) on {self.device}...")
        try:
            self.model = SentenceTransformer(model_name, device=self.device, local_files_only=True)
        except Exception:
            try:
                self.model = SentenceTransformer(model_name, device=self.device)
            except Exception:
                self.device = "cpu"
                self.model = SentenceTransformer(model_name, device="cpu")
        print("Evidence Retriever ready!")

    def retrieve(
        self,
        claim: str,
        source_text: str,
        genre: str = "news",
        top_k: int = 5,
        min_similarity: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the top-k most similar sentences/turns from source_text for the given claim.
        Applies relevance filtering: prunes sentences with similarity < min_similarity,
        while always guaranteeing at least the top-1 sentence as an anchor.
        Returns a list of dicts: [{"sentence": str, "score": float, "rank": int}]
        """
        units = split_source_into_units(source_text, genre=genre)
        if not units:
            return []

        # If fewer units than top_k, return all units
        k = min(top_k, len(units))

        claim_emb = self.model.encode(claim, convert_to_tensor=True, device=self.device)
        unit_embs = self.model.encode(units, convert_to_tensor=True, device=self.device)

        cos_scores = util.cos_sim(claim_emb, unit_embs)[0]
        top_results = torch.topk(cos_scores, k=k)

        retrieved = []
        for rank, (score, idx) in enumerate(zip(top_results.values, top_results.indices), start=1):
            retrieved.append({
                "rank": rank,
                "sentence": units[idx.item()],
                "score": round(score.item(), 4),
            })

        # Strategy 3: Relevance filtering (prune sentences below min_similarity)
        if min_similarity is not None and min_similarity > 0.0:
            filtered = [r for r in retrieved if r["score"] >= min_similarity]
            # Safeguard: always retain at least the single best sentence (top-1) as anchor
            return filtered if filtered else [retrieved[0]]

        return retrieved
