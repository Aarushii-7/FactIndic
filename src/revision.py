"""
FactIndic - Phase 5: Targeted Revision Engine
Revises problematic claim groups using retrieved source evidence while preserving
independently supported context, strictly adhering to Section 11 of the FactIndic Guide.
"""

from typing import Dict, Any, List

PROMPT_TARGETED_REVISION = """You are a precision factuality revision assistant.
Your task is to revise a summary so that all facts are 100% faithful to the source document.

SOURCE DOCUMENT:
{source_text}

CURRENT SUMMARY:
{current_summary}

PROBLEMATIC CLAIMS & SOURCE EVIDENCE:
{problematic_claims_text}

REVISION INSTRUCTIONS:
1. Correct the contradicted claims using the exact facts from the source evidence.
2. Remove any neutral/unsupported claims that cannot be verified from the source.
3. PRESERVE all supported claims and maintain coherent, concise prose.
4. Do NOT add new external facts not present in the source.
5. Output ONLY the revised summary text without any preamble, explanation, or bullet points.

REVISED SUMMARY:"""

class TargetedReviser:
    def __init__(self, pipe=None):
        self.pipe = pipe

    def format_problematic_claims(self, graph_context: Dict[str, Any]) -> str:
        lines = []
        for c in graph_context["claim_details"]:
            cid = c["claim_id"]
            status = c["nli_label"].upper()
            role = c["role"]
            text = c["claim_text"]
            evidence = c["retrieved_evidence"]

            if c["is_flagged"]:
                lines.append(f"- Claim [{cid}] ({status} - {role}): \"{text}\"")
                lines.append(f"  Source Evidence: \"{evidence}\"")
            else:
                lines.append(f"- Connected Claim [{cid}] (SUPPORTED - {role}): \"{text}\" (Keep unchanged)")

        return "\n".join(lines)

    def revise(
        self,
        source_text: str,
        current_summary: str,
        graph_context: Dict[str, Any],
    ) -> str:
        """
        Executes a targeted revision using the local LLM.
        """
        claims_text = self.format_problematic_claims(graph_context)
        prompt = PROMPT_TARGETED_REVISION.format(
            source_text=source_text.strip(),
            current_summary=current_summary.strip(),
            problematic_claims_text=claims_text,
        )

        if self.pipe is not None:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert factuality editor. Revise the summary strictly using the provided source evidence. "
                        "Output ONLY the revised summary text."
                    ),
                },
                {"role": "user", "content": prompt},
            ]
            outputs = self.pipe(
                messages,
                max_new_tokens=250,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.pipe.tokenizer.eos_token_id,
            )
            revised = outputs[0]["generated_text"][-1]["content"].strip()
            return revised

        # Fallback if no LLM pipe is provided
        return current_summary
