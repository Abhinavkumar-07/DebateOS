"""
DebateOS State Models
All Pydantic models for debate state, events, and agent outputs.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import uuid


# ─── Event Types ───────────────────────────────────────────────

class EventType(str, Enum):
    PRO_ARGUMENT = "PRO_ARGUMENT"
    PRO_FALLACY = "PRO_FALLACY"
    DEF_ARGUMENT = "DEF_ARGUMENT"
    DEF_FALLACY = "DEF_FALLACY"
    JUDGE_RESULT = "JUDGE_RESULT"
    ROUND_SUMMARY = "ROUND_SUMMARY"
    FINAL_VERDICT = "FINAL_VERDICT"
    DEBATE_START = "DEBATE_START"
    ERROR = "ERROR"


# ─── Agent Output Models ─────────────────────────────────────

class ProArgument(BaseModel):
    """Prosecutor agent structured output."""
    point: str = ""
    evidence: str = ""
    inference: str = ""


class DefArgument(BaseModel):
    """Defender agent structured output."""
    counter_point: str = ""
    weakness_exposed: str = ""
    alternative_evidence: str = ""


class FallacyResult(BaseModel):
    """Fallacy detection result."""
    fallacy_detected: bool = False
    type: Optional[str] = None
    severity: int = 0
    explanation: Optional[str] = None
    quote: Optional[str] = None


class AgentScores(BaseModel):
    """Scores for a single agent."""
    logic_score: float = Field(default=0, ge=0, le=10)
    evidence_score: float = Field(default=0, ge=0, le=10)
    rhetoric_score: float = Field(default=0, ge=0, le=10)


class JudgeResult(BaseModel):
    """Judge evaluation output."""
    pro_scores: AgentScores = Field(default_factory=AgentScores)
    def_scores: AgentScores = Field(default_factory=AgentScores)
    pro_fallacy_penalty: float = 0
    def_fallacy_penalty: float = 0
    pro_final_score: float = 0
    def_final_score: float = 0
    winner: str = "PRO"
    confidence: float = Field(default=50, ge=0, le=100)
    reasoning: str = ""


class RoundSummary(BaseModel):
    """Summary emitted after each round."""
    round: int
    winner: str
    pro_final_score: float
    def_final_score: float
    pro_scores: dict = {}
    def_scores: dict = {}
    pro_fallacies: List[dict] = []
    def_fallacies: List[dict] = []
    early_stop: bool = False


class FinalVerdict(BaseModel):
    """Final debate verdict."""
    winner: str
    total_rounds_played: int
    pro_total_score: float
    def_total_score: float
    pro_round_wins: int
    def_round_wins: int
    confidence: float
    summary: str
    all_scores: List[dict] = []
    all_fallacies: List[dict] = []


# ─── Event Wrapper ─────────────────────────────────────────────

class DebateEvent(BaseModel):
    """A single SSE event in the debate stream."""
    event_type: EventType
    round: Optional[int] = None
    agent: str
    content: dict
    metadata: dict = {}


# ─── Debate State ──────────────────────────────────────────────

class DebateState(BaseModel):
    """Full state of a debate session."""
    debate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    claim: str
    total_rounds: int = 3
    current_round: int = 0
    pro_args: List[dict] = []
    def_args: List[dict] = []
    pro_fallacies: List[dict] = []
    def_fallacies: List[dict] = []
    scores: List[dict] = []
    round_summaries: List[dict] = []
    verdict: Optional[dict] = None
    status: str = "pending"  # pending, running, completed, error
    early_stopped: bool = False
