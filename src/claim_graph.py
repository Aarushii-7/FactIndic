"""
FactIndic - Phase 5: Related Claims & Claim Graph (Approach C)
Builds a structured NetworkX graph of claim dependencies based on shared entities,
dates, numbers, and coreference cues as specified in Section 10 of the FactIndic Guide.
Extracts connected subgraphs for targeted revision so context is preserved without overconnection.
"""

import re
from typing import List, Dict, Any, Set
import networkx as nx

def extract_content_tokens(text: str) -> Set[str]:
    """Extracts informative tokens (nouns, entities, numbers, dates) for dependency linking."""
    # Find all words with 3+ characters or digits
    tokens = set(re.findall(r"\b[A-Za-z0-9\u0900-\u097F]{3,}\b", text.lower()))
    # Remove common stop words (both English and Hindi transliterations)
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "was", "were", "will",
        "hai", "aur", "mein", "liye", "par", "tha", "thi", "gaya", "kare", "kaha"
    }
    return tokens - stopwords

class ClaimGraph:
    def __init__(self, claim_records: List[Dict[str, Any]]):
        self.graph = nx.Graph()
        self.claims_by_id = {}

        # Add nodes with claim metadata
        for c in claim_records:
            cid = c["claim_id"]
            self.claims_by_id[cid] = c
            self.graph.add_node(
                cid,
                claim_text=c["claim_text"],
                nli_label=c.get("nli_label", "unknown"),
                retrieved_evidence=c.get("retrieved_evidence", ""),
                tokens=extract_content_tokens(c["claim_text"]),
            )

        # Add edges between claims that share entities, dates, or numbers
        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                tokens1 = self.graph.nodes[n1]["tokens"]
                tokens2 = self.graph.nodes[n2]["tokens"]
                shared = tokens1.intersection(tokens2)

                # Connect if they share entities/numbers/dates
                if len(shared) >= 1:
                    self.graph.add_edge(n1, n2, relation="shared_context", shared_terms=list(shared))

    def get_related_claims(self, flagged_claim_ids: List[str]) -> Dict[str, Any]:
        """
        Given a list of problematic/flagged claim IDs, finds directly connected neighbor claims.
        Returns:
            {
                "flagged_ids": [...],
                "dependent_ids": [...],
                "all_revision_ids": [...],
                "claim_details": [...],
            }
        """
        flagged_set = set(flagged_claim_ids)
        dependent_set = set()

        for fid in flagged_set:
            if fid in self.graph:
                neighbors = set(self.graph.neighbors(fid))
                dependent_set.update(neighbors - flagged_set)

        all_revision_ids = sorted(list(flagged_set | dependent_set))

        details = []
        for cid in all_revision_ids:
            node_data = self.graph.nodes[cid]
            is_flagged = cid in flagged_set
            details.append({
                "claim_id": cid,
                "is_flagged": is_flagged,
                "role": "needs_correction" if is_flagged else "preserve_context",
                "claim_text": node_data["claim_text"],
                "nli_label": node_data["nli_label"],
                "retrieved_evidence": node_data["retrieved_evidence"],
            })

        return {
            "flagged_ids": sorted(list(flagged_set)),
            "dependent_ids": sorted(list(dependent_set)),
            "all_revision_ids": all_revision_ids,
            "claim_details": details,
        }
