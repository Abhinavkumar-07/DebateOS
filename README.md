# DebateOS ⚡

**Adversarial Multi-Agent AI Debate System with Real-Time Fallacy Detection**

DebateOS pits AI agents against each other in a structured debate. A Prosecutor argues FOR a claim, a Defender argues AGAINST, and every argument gets scanned for logical fallacies in real-time. A Judge agent evaluates both sides and produces a final verdict.

## 🏗️ Architecture

```
User → Prosecutor → Fallacy Detection → Defender → Fallacy Detection → Judge → Next Round → Final Verdict
```

### Agents
| Agent | Role |
|-------|------|
| **Prosecutor** | Argues FOR the claim (isolated — only sees own history) |
| **Defender** | Argues AGAINST (isolated — only sees latest PRO argument) |
| **Fallacy Detector** | Analyzes every argument for 5 fallacy types |
| **Judge** | Scores logic, evidence, rhetoric with fallacy penalties |

### Scoring Formula
```
final_score = logic_score + evidence_score + rhetoric_score - fallacy_penalty
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set your API key
# Edit .env file and replace 'your_gemini_api_key_here' with your actual key
# Get a free key at: https://aistudio.google.com/apikey

# Start server
python main.py
```

Backend runs at: `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at: `http://localhost:5173`

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/debate/start` | POST | Start a new debate — returns `debate_id` |
| `/debate/{id}/stream` | GET | SSE stream of debate events |
| `/debate/{id}/status` | GET | Get current debate state |
| `/health` | GET | Health check |

## 📁 Project Structure

```
backend/
├── agents/           # AI agent implementations
│   ├── base.py       # LLM abstraction (Gemini/OpenAI)
│   ├── prosecutor.py # FOR the claim
│   ├── defender.py   # AGAINST the claim
│   ├── fallacy_detector.py
│   └── judge.py      # Scoring with penalties
├── graph/
│   ├── debate_state.py  # Pydantic models
│   └── debate_loop.py   # Async orchestration
├── api/
│   └── routes.py     # FastAPI endpoints + SSE
├── prompts/          # Agent system prompts
├── config.py         # Environment settings
└── main.py           # FastAPI app entry

frontend/
├── src/
│   ├── hooks/
│   │   └── useDebateStream.js  # SSE hook
│   └── components/
│       ├── ClaimInput.jsx      # Claim + demo buttons
│       ├── DebateArena.jsx     # Main layout
│       ├── AgentPanel.jsx      # PRO/DEF columns
│       ├── ArgumentBubble.jsx  # Argument cards
│       ├── FallacyAlert.jsx    # Live fallacy alerts
│       ├── ScoreTracker.jsx    # Score bars
│       ├── JudgePanel.jsx      # Judge reasoning
│       ├── VerdictCard.jsx     # Final verdict modal
│       └── ThinkingIndicator.jsx
└── vite.config.js
```

## ⚙️ Configuration

Set in `backend/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `gemini` | `gemini` or `openai` |
| `GEMINI_API_KEY` | — | Your Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Model to use |
| `MAX_ROUNDS` | `3` | Max debate rounds |
| `EARLY_STOP_CONFIDENCE` | `85` | Stop early if confidence > this |

## 🎮 Demo Claims

The UI preloads 3 demo claims:
- "AI will replace programmers"
- "Social media is harmful to society"
- "Remote work is better than office work"

## 🔑 Key Features

- **Strict Agent Isolation**: PRO and DEF never share context
- **Real-Time Fallacy Detection**: Runs after EVERY argument
- **Deterministic Scoring**: Fallacy penalties computed in code, not by LLM
- **Early Stopping**: Debate ends if judge confidence > 85%
- **SSE Streaming**: Live event-driven UI updates
- **Round Summaries**: Clean sync points after each round
