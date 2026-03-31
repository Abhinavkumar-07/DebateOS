"""
DebateOS Debate Loop
Async generator orchestrating the full debate flow with early stopping.
Flow: PRO → Fallacy → DEF → Fallacy → Judge → Round Summary → [repeat or stop]
"""

import logging
import asyncio
from typing import AsyncGenerator

from agents.prosecutor import ProsecutorAgent
from agents.defender import DefenderAgent
from agents.fallacy_detector import FallacyDetectorAgent
from agents.judge import JudgeAgent
from graph.debate_state import (
    DebateState,
    DebateEvent,
    EventType,
    FinalVerdict,
)
from config import settings

logger = logging.getLogger(__name__)

# ─── Agent Singletons ──────────────────────────────────────────
prosecutor = ProsecutorAgent()
defender = DefenderAgent()
fallacy_detector = FallacyDetectorAgent()
judge = JudgeAgent()


async def run_debate(state: DebateState) -> AsyncGenerator[DebateEvent, None]:
    """
    Run the full debate loop as an async generator.
    Yields DebateEvent objects for SSE streaming.

    Implements:
    - Turn-based isolation (PRO sees only own history, DEF sees only latest PRO)
    - Fallacy detection after EVERY agent turn
    - Judge scoring with deterministic fallacy penalties
    - Early stopping when confidence > threshold
    - Round summaries after each complete round
    """

    state.status = "running"

    # Emit debate start
    yield DebateEvent(
        event_type=EventType.DEBATE_START,
        round=0,
        agent="system",
        content={"claim": state.claim, "total_rounds": state.total_rounds},
        metadata={"debate_id": state.debate_id},
    )

    round_winners = []

    for round_num in range(1, state.total_rounds + 1):
        state.current_round = round_num
        logger.info(f"Starting Round {round_num}/{state.total_rounds}")

        try:
            # ── Step 1: Prosecutor argues ──────────────────────────
            # PRO only sees: claim + its own past arguments (STRICT ISOLATION)
            pro_arg = await prosecutor.argue(
                claim=state.claim,
                past_arguments=state.pro_args,  # Only own history
            )
            state.pro_args.append(pro_arg)

            yield DebateEvent(
                event_type=EventType.PRO_ARGUMENT,
                round=round_num,
                agent="prosecutor",
                content=pro_arg,
                metadata={"turn": "prosecutor", "round": round_num},
            )

            # Rate limit delay (Gemini free tier: ~15 RPM)
            await asyncio.sleep(5)

            # ── Step 2: Fallacy check on PRO ──────────────────────
            pro_fallacy = await fallacy_detector.analyze(pro_arg, agent_role="prosecutor")
            state.pro_fallacies.append(pro_fallacy)

            yield DebateEvent(
                event_type=EventType.PRO_FALLACY,
                round=round_num,
                agent="fallacy_detector",
                content=pro_fallacy,
                metadata={"target": "prosecutor", "round": round_num},
            )

            # Rate limit delay
            await asyncio.sleep(5)

            # ── Step 3: Defender responds ─────────────────────────
            # DEF only sees: claim + latest PRO argument (STRICT ISOLATION)
            def_arg = await defender.argue(
                claim=state.claim,
                latest_pro_argument=pro_arg,  # Only latest, not history
            )
            state.def_args.append(def_arg)

            yield DebateEvent(
                event_type=EventType.DEF_ARGUMENT,
                round=round_num,
                agent="defender",
                content=def_arg,
                metadata={"turn": "defender", "round": round_num},
            )

            # Rate limit delay
            await asyncio.sleep(5)

            # ── Step 4: Fallacy check on DEF ──────────────────────
            def_fallacy = await fallacy_detector.analyze(def_arg, agent_role="defender")
            state.def_fallacies.append(def_fallacy)

            yield DebateEvent(
                event_type=EventType.DEF_FALLACY,
                round=round_num,
                agent="fallacy_detector",
                content=def_fallacy,
                metadata={"target": "defender", "round": round_num},
            )

            # Rate limit delay
            await asyncio.sleep(5)

            # ── Step 5: Judge evaluates ───────────────────────────
            judge_result = await judge.evaluate(
                claim=state.claim,
                pro_argument=pro_arg,
                def_argument=def_arg,
                pro_fallacy=pro_fallacy,
                def_fallacy=def_fallacy,
                round_num=round_num,
            )
            state.scores.append(judge_result)

            yield DebateEvent(
                event_type=EventType.JUDGE_RESULT,
                round=round_num,
                agent="judge",
                content=judge_result,
                metadata={"round": round_num},
            )

            # ── Step 6: Round Summary ─────────────────────────────
            round_summary = {
                "round": round_num,
                "winner": judge_result["winner"],
                "pro_final_score": judge_result["pro_final_score"],
                "def_final_score": judge_result["def_final_score"],
                "pro_scores": judge_result["pro_scores"],
                "def_scores": judge_result["def_scores"],
                "pro_fallacies": [pro_fallacy],
                "def_fallacies": [def_fallacy],
                "early_stop": False,
            }
            round_winners.append(judge_result["winner"])
            state.round_summaries.append(round_summary)

            # ── Step 7: Early Stopping Check ──────────────────────
            if judge_result["confidence"] > settings.EARLY_STOP_CONFIDENCE:
                round_summary["early_stop"] = True
                logger.info(
                    f"Early stop triggered at Round {round_num} "
                    f"(confidence: {judge_result['confidence']}%)"
                )
                state.early_stopped = True

                yield DebateEvent(
                    event_type=EventType.ROUND_SUMMARY,
                    round=round_num,
                    agent="system",
                    content=round_summary,
                    metadata={"early_stop": True, "confidence": judge_result["confidence"]},
                )
                break
            else:
                yield DebateEvent(
                    event_type=EventType.ROUND_SUMMARY,
                    round=round_num,
                    agent="system",
                    content=round_summary,
                    metadata={"early_stop": False},
                )

        except Exception as e:
            logger.error(f"Error in debate round {round_num}: {e}", exc_info=True)
            yield DebateEvent(
                event_type=EventType.ERROR,
                round=round_num,
                agent="system",
                content={"error": str(e), "round": round_num},
                metadata={"recoverable": False},
            )
            state.status = "error"
            return

    # ── Final Verdict ─────────────────────────────────────────────
    verdict = _compute_final_verdict(state, round_winners)
    state.verdict = verdict
    state.status = "completed"

    yield DebateEvent(
        event_type=EventType.FINAL_VERDICT,
        round=None,
        agent="judge",
        content=verdict,
        metadata={"debate_id": state.debate_id, "early_stopped": state.early_stopped},
    )


def _compute_final_verdict(state: DebateState, round_winners: list[str]) -> dict:
    """
    Compute the final debate verdict from all rounds.
    Aggregates scores and determines overall winner.
    """
    pro_total = sum(s.get("pro_final_score", 0) for s in state.scores)
    def_total = sum(s.get("def_final_score", 0) for s in state.scores)
    pro_wins = round_winners.count("PRO")
    def_wins = round_winners.count("DEF")
    rounds_played = len(state.scores)

    # Overall winner based on total scores
    if pro_total > def_total:
        winner = "PRO"
    elif def_total > pro_total:
        winner = "DEF"
    else:
        # Tiebreaker: who won more rounds
        winner = "PRO" if pro_wins >= def_wins else "DEF"

    # Compute average confidence
    avg_confidence = sum(s.get("confidence", 50) for s in state.scores) / max(len(state.scores), 1)

    # Generate summary
    margin = abs(pro_total - def_total)
    if margin > 10:
        strength = "decisively"
    elif margin > 5:
        strength = "convincingly"
    elif margin > 2:
        strength = "narrowly"
    else:
        strength = "by a razor-thin margin"

    winner_name = "Prosecutor" if winner == "PRO" else "Defender"
    summary = (
        f"After {rounds_played} round{'s' if rounds_played > 1 else ''}, "
        f"the {winner_name} wins {strength} with a total score of "
        f"{max(pro_total, def_total):.1f} vs {min(pro_total, def_total):.1f}. "
    )

    if state.early_stopped:
        summary += f"The debate ended early due to high confidence in Round {rounds_played}. "

    # Count total fallacies
    pro_fallacy_count = sum(1 for f in state.pro_fallacies if f.get("fallacy_detected"))
    def_fallacy_count = sum(1 for f in state.def_fallacies if f.get("fallacy_detected"))
    if pro_fallacy_count or def_fallacy_count:
        summary += (
            f"Fallacies detected: Prosecutor ({pro_fallacy_count}), "
            f"Defender ({def_fallacy_count})."
        )

    return {
        "winner": winner,
        "total_rounds_played": rounds_played,
        "pro_total_score": round(pro_total, 1),
        "def_total_score": round(def_total, 1),
        "pro_round_wins": pro_wins,
        "def_round_wins": def_wins,
        "confidence": round(avg_confidence, 1),
        "summary": summary,
        "all_scores": state.scores,
        "all_fallacies": {
            "prosecutor": state.pro_fallacies,
            "defender": state.def_fallacies,
        },
    }
