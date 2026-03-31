"""
DebateOS Judge Agent
Evaluates both sides fairly. Final scoring includes fallacy penalties.
Formula: final_score = logic_score + evidence_score + rhetoric_score - fallacy_penalty
"""

import json
from agents.base import BaseAgent


class JudgeAgent(BaseAgent):
    """Judge: evaluates both arguments, applies fallacy penalties, determines winner."""

    def __init__(self):
        super().__init__("judge.txt")

    async def evaluate(
        self,
        claim: str,
        pro_argument: dict,
        def_argument: dict,
        pro_fallacy: dict,
        def_fallacy: dict,
        round_num: int,
    ) -> dict:
        """
        Evaluate both sides and produce scores with fallacy penalties.

        Args:
            claim: The debate claim.
            pro_argument: Prosecutor's argument for this round.
            def_argument: Defender's argument for this round.
            pro_fallacy: Fallacy analysis of prosecutor's argument.
            def_fallacy: Fallacy analysis of defender's argument.
            round_num: Current round number.

        Returns:
            Complete judge result with scores, penalties, winner, confidence.
        """
        prompt = f"CLAIM: \"{claim}\"\nROUND: {round_num}\n\n"

        prompt += "=== PROSECUTOR'S ARGUMENT ===\n"
        prompt += f"Point: {pro_argument.get('point', 'N/A')}\n"
        prompt += f"Evidence: {pro_argument.get('evidence', 'N/A')}\n"
        prompt += f"Inference: {pro_argument.get('inference', 'N/A')}\n\n"

        prompt += "=== DEFENDER'S ARGUMENT ===\n"
        prompt += f"Counter-Point: {def_argument.get('counter_point', 'N/A')}\n"
        prompt += f"Weakness Exposed: {def_argument.get('weakness_exposed', 'N/A')}\n"
        prompt += f"Alternative Evidence: {def_argument.get('alternative_evidence', 'N/A')}\n\n"

        # Include fallacy context for the judge's awareness
        prompt += "=== FALLACY ANALYSIS (for context) ===\n"
        if pro_fallacy.get("fallacy_detected"):
            prompt += f"Prosecutor fallacy: {pro_fallacy.get('type')} (severity {pro_fallacy.get('severity')})\n"
            prompt += f"  Explanation: {pro_fallacy.get('explanation')}\n"
        else:
            prompt += "Prosecutor: No fallacies detected\n"

        if def_fallacy.get("fallacy_detected"):
            prompt += f"Defender fallacy: {def_fallacy.get('type')} (severity {def_fallacy.get('severity')})\n"
            prompt += f"  Explanation: {def_fallacy.get('explanation')}\n"
        else:
            prompt += "Defender: No fallacies detected\n"

        prompt += "\nScore both sides on logic, evidence, and rhetoric (0-10 each). "
        prompt += "Do NOT factor fallacies into scores — penalties are applied separately.\n"
        prompt += "\nRespond with ONLY the JSON object."

        result = await self.call_llm(prompt)

        # Extract and validate scores
        pro_scores = result.get("pro_scores", {})
        def_scores = result.get("def_scores", {})

        pro_logic = self._clamp(pro_scores.get("logic_score", 5), 0, 10)
        pro_evidence = self._clamp(pro_scores.get("evidence_score", 5), 0, 10)
        pro_rhetoric = self._clamp(pro_scores.get("rhetoric_score", 5), 0, 10)

        def_logic = self._clamp(def_scores.get("logic_score", 5), 0, 10)
        def_evidence = self._clamp(def_scores.get("evidence_score", 5), 0, 10)
        def_rhetoric = self._clamp(def_scores.get("rhetoric_score", 5), 0, 10)

        # Compute fallacy penalties deterministically
        pro_penalty = pro_fallacy.get("severity", 0) if pro_fallacy.get("fallacy_detected") else 0
        def_penalty = def_fallacy.get("severity", 0) if def_fallacy.get("fallacy_detected") else 0

        # Final score formula: logic + evidence + rhetoric - fallacy_penalty
        pro_final = pro_logic + pro_evidence + pro_rhetoric - pro_penalty
        def_final = def_logic + def_evidence + def_rhetoric - def_penalty

        # Determine winner based on final scores (overrides LLM's opinion)
        winner = "PRO" if pro_final >= def_final else "DEF"

        confidence = self._clamp(result.get("confidence", 50), 0, 100)

        return {
            "pro_scores": {
                "logic_score": pro_logic,
                "evidence_score": pro_evidence,
                "rhetoric_score": pro_rhetoric,
            },
            "def_scores": {
                "logic_score": def_logic,
                "evidence_score": def_evidence,
                "rhetoric_score": def_rhetoric,
            },
            "pro_fallacy_penalty": pro_penalty,
            "def_fallacy_penalty": def_penalty,
            "pro_final_score": round(pro_final, 1),
            "def_final_score": round(def_final, 1),
            "winner": winner,
            "confidence": confidence,
            "reasoning": result.get("reasoning", "No reasoning provided."),
        }

    @staticmethod
    def _clamp(value, min_val, max_val):
        """Clamp a value to a range."""
        try:
            return max(min_val, min(max_val, float(value)))
        except (ValueError, TypeError):
            return (min_val + max_val) / 2
