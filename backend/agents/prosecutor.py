"""
DebateOS Prosecutor Agent
Argues IN FAVOR of the claim. Strictly isolated — only sees its own past arguments.
"""

import json
from agents.base import BaseAgent


class ProsecutorAgent(BaseAgent):
    """Prosecutor: argues FOR the claim with structured output."""

    def __init__(self):
        super().__init__("prosecutor.txt")

    async def argue(self, claim: str, past_arguments: list[dict]) -> dict:
        """
        Generate an argument supporting the claim.

        Args:
            claim: The debate claim.
            past_arguments: This agent's own previous arguments (strict isolation).

        Returns:
            Dict with point, evidence, inference.
        """
        prompt = f"CLAIM TO SUPPORT: \"{claim}\"\n\n"

        if past_arguments:
            prompt += "YOUR PREVIOUS ARGUMENTS (build upon these, do not repeat):\n"
            for i, arg in enumerate(past_arguments, 1):
                prompt += f"\n--- Round {i} ---\n"
                prompt += f"Point: {arg.get('point', 'N/A')}\n"
                prompt += f"Evidence: {arg.get('evidence', 'N/A')}\n"
                prompt += f"Inference: {arg.get('inference', 'N/A')}\n"
            prompt += f"\n\nThis is Round {len(past_arguments) + 1}. "
            prompt += "Present a NEW angle or deeper evidence. Do NOT repeat previous points.\n"
        else:
            prompt += "This is Round 1 — your opening argument. Make a strong foundational case.\n"

        prompt += "\nRespond with ONLY the JSON object."

        result = await self.call_llm(prompt)

        # Ensure required fields exist
        return {
            "point": result.get("point", result.get("raw_text", "Failed to generate argument")),
            "evidence": result.get("evidence", ""),
            "inference": result.get("inference", ""),
        }
