"""
DebateOS API Routes
POST /debate/start → creates debate, returns debate_id
GET  /debate/{id}/stream → SSE stream of debate events
GET  /debate/{id}/status → current debate state
"""

import json
import asyncio
import logging
from typing import Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from graph.debate_state import DebateState
from graph.debate_loop import run_debate
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debate", tags=["debate"])

# ─── In-Memory State Store ─────────────────────────────────────
# Hackathon-friendly: no database needed
debates: Dict[str, DebateState] = {}


# ─── Request/Response Models ──────────────────────────────────

class StartDebateRequest(BaseModel):
    claim: str
    rounds: int = 3


class StartDebateResponse(BaseModel):
    debate_id: str
    claim: str
    rounds: int
    status: str


class DebateStatusResponse(BaseModel):
    debate_id: str
    claim: str
    status: str
    current_round: int
    total_rounds: int
    pro_args: list
    def_args: list
    scores: list
    verdict: dict | None


# ─── Endpoints ────────────────────────────────────────────────

@router.post("/start", response_model=StartDebateResponse)
async def start_debate(request: StartDebateRequest):
    """
    Start a new debate. Returns debate_id for streaming.
    """
    if not request.claim.strip():
        raise HTTPException(status_code=400, detail="Claim cannot be empty")

    rounds = max(1, min(request.rounds, 5))  # Clamp to 1-5

    state = DebateState(
        claim=request.claim.strip(),
        total_rounds=rounds,
    )
    debates[state.debate_id] = state

    logger.info(f"Debate created: {state.debate_id} — \"{state.claim}\" ({rounds} rounds)")

    return StartDebateResponse(
        debate_id=state.debate_id,
        claim=state.claim,
        rounds=rounds,
        status="pending",
    )


@router.get("/{debate_id}/stream")
async def stream_debate(debate_id: str):
    """
    SSE stream of debate events.
    The debate runs asynchronously and emits events as they happen.
    """
    if debate_id not in debates:
        raise HTTPException(status_code=404, detail="Debate not found")

    state = debates[debate_id]

    if state.status == "completed":
        raise HTTPException(status_code=400, detail="Debate already completed")

    if state.status == "running":
        raise HTTPException(status_code=400, detail="Debate already in progress")

    async def event_generator():
        """Generate SSE events from the debate loop."""
        try:
            async for event in run_debate(state):
                event_data = event.model_dump()
                sse_line = f"event: {event.event_type.value}\ndata: {json.dumps(event_data)}\n\n"
                yield sse_line

                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Stream error for debate {debate_id}: {e}", exc_info=True)
            error_data = {
                "event_type": "ERROR",
                "round": None,
                "agent": "system",
                "content": {"error": str(e)},
                "metadata": {},
            }
            yield f"event: ERROR\ndata: {json.dumps(error_data)}\n\n"

        # Signal stream end
        yield f"event: STREAM_END\ndata: {json.dumps({'status': 'completed'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/{debate_id}/status", response_model=DebateStatusResponse)
async def get_debate_status(debate_id: str):
    """Get the current state of a debate."""
    if debate_id not in debates:
        raise HTTPException(status_code=404, detail="Debate not found")

    state = debates[debate_id]

    return DebateStatusResponse(
        debate_id=state.debate_id,
        claim=state.claim,
        status=state.status,
        current_round=state.current_round,
        total_rounds=state.total_rounds,
        pro_args=state.pro_args,
        def_args=state.def_args,
        scores=state.scores,
        verdict=state.verdict,
    )


@router.get("/list/all")
async def list_debates():
    """List all debates (debug endpoint)."""
    return {
        "debates": [
            {
                "debate_id": d.debate_id,
                "claim": d.claim,
                "status": d.status,
                "current_round": d.current_round,
            }
            for d in debates.values()
        ]
    }
