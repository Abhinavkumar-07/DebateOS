"""
DebateOS — Main Application Entry Point
Adversarial Multi-Agent AI Debate System
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from config import settings

# ─── Logging Setup ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("debateos")

# ─── FastAPI App ──────────────────────────────────────────────
app = FastAPI(
    title="DebateOS",
    description="Adversarial Multi-Agent AI Debate System with Real-Time Fallacy Detection",
    version="1.0.0",
)

# ─── CORS Middleware ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Mount Routes ─────────────────────────────────────────────
app.include_router(router)


# ─── Root Endpoint ────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": "DebateOS",
        "version": "1.0.0",
        "description": "Adversarial Multi-Agent AI Debate System",
        "endpoints": {
            "start_debate": "POST /debate/start",
            "stream_debate": "GET /debate/{id}/stream",
            "debate_status": "GET /debate/{id}/status",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "model": settings.GEMINI_MODEL if settings.LLM_PROVIDER == "gemini" else settings.OPENAI_MODEL,
    }


# ─── Startup Events ──────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info("  DebateOS — Starting Up")
    logger.info(f"  LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"  Model: {settings.GEMINI_MODEL if settings.LLM_PROVIDER == 'gemini' else settings.OPENAI_MODEL}")
    logger.info(f"  Max Rounds: {settings.MAX_ROUNDS}")
    logger.info(f"  Early Stop Confidence: {settings.EARLY_STOP_CONFIDENCE}%")
    logger.info("=" * 60)

    # Validate API key is set
    if settings.LLM_PROVIDER == "gemini" and not settings.GEMINI_API_KEY:
        logger.warning("⚠️  GEMINI_API_KEY not set! Set it in .env file.")
    elif settings.LLM_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
        logger.warning("⚠️  OPENAI_API_KEY not set! Set it in .env file.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

