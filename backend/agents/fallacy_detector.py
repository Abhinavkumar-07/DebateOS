"""
DebateOS Fallacy Detector Agent
Analyzes any argument for logical fallacies. Runs after EVERY agent turn.
"""

import json
from agents.base import BaseAgent


class FallacyDetectorAgent(BaseAgent):
    """Fallacy Detector: analyzes arguments for 5 types of logical fallacies."""

    def __init__(self):
        super().__init__("fallacy_detector.txt")

    async def analyze(self, argument: dict, agent_role: str = "unknown") -> dict:
        """
        Analyze an argument for logical fallacies.

        Args:
            argument: The argument dict to analyze.
            agent_role: "prosecutor" or "defender" — for context.

        Returns:
            Dict with fallacy_detected, type, severity, explanation, quote.
        """
        # Flatten argument into readable text for analysis
        if "point" in argument:
            # Prosecutor format
            arg_text = (
                f"POINT: {argument.get('point', '')}\n"
                f"EVIDENCE: {argument.get('evidence', '')}\n"
                f"INFERENCE: {argument.get('inference', '')}"
            )
        elif "counter_point" in argument:
            # Defender format
            arg_text = (
                f"COUNTER-POINT: {argument.get('counter_point', '')}\n"
                f"WEAKNESS EXPOSED: {argument.get('weakness_exposed', '')}\n"
                f"ALTERNATIVE EVIDENCE: {argument.get('alternative_evidence', '')}"
            )
        else:
            # Generic fallback
            arg_text = json.dumps(argument, indent=2)

        prompt = f"ARGUMENT BY {agent_role.upper()} TO ANALYZE:\n\n{arg_text}\n\n"
        prompt += "Analyze this argument for logical fallacies. "
        prompt += "Check for: Strawman, Weak Evidence, False Dichotomy, Ad Hominem, Logical Inconsistency.\n"
        prompt += "If the argument is sound, set fallacy_detected to false.\n"
        prompt += "\nRespond with ONLY the JSON object."

        result = await self.call_llm(prompt)

        # Normalize and validate output
        return {
            "fallacy_detected": bool(result.get("fallacy_detected", False)),
            "type": result.get("type", None),
            "severity": min(5, max(0, int(result.get("severity", 0)))),
            "explanation": result.get("explanation", None),
            "quote": result.get("quote", None),
        }
