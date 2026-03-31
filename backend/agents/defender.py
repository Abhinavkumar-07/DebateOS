"""
DebateOS Defender Agent
Argues AGAINST the claim by countering the Prosecutor's latest argument.
Strictly isolated — only sees the latest PRO argument, not full history.
"""

import json
from agents.base import BaseAgent


class DefenderAgent(BaseAgent):
    """Defender: argues AGAINST the claim by countering the latest PRO argument."""

    def __init__(self):
        super().__init__("defender.txt")

    async def argue(self, claim: str, latest_pro_argument: dict) -> dict:
        """
        Generate a counter-argument against the latest prosecutor argument.

        Args:
            claim: The debate claim.
            latest_pro_argument: The Prosecutor's most recent argument (strict isolation).

        Returns:
            Dict with counter_point, weakness_exposed, alternative_evidence.
        """
        prompt = f"CLAIM BEING DEBATED: \"{claim}\"\n\n"
        prompt += "PROSECUTOR'S LATEST ARGUMENT (counter this directly):\n"
        prompt += f"Point: {latest_pro_argument.get('point', 'N/A')}\n"
        prompt += f"Evidence: {latest_pro_argument.get('evidence', 'N/A')}\n"
        prompt += f"Inference: {latest_pro_argument.get('inference', 'N/A')}\n"
        prompt += "\nDirectly counter the above argument. Find weaknesses and provide alternative evidence.\n"
        prompt += "\nRespond with ONLY the JSON object."

        result = await self.call_llm(prompt)

        # Ensure required fields exist
        return {
            "counter_point": result.get("counter_point", result.get("raw_text", "Failed to generate counter-argument")),
            "weakness_exposed": result.get("weakness_exposed", ""),
            "alternative_evidence": result.get("alternative_evidence", ""),
        }
