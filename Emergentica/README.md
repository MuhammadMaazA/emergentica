#  Emergentica - AI-Powered Emergency Dispatch System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-green.svg)](https://github.com/langchain-ai/langgraph)

** The Great Agent Hack 2025 - Track A: Iron Man (Performance & Robustness)**

A production-ready, voice-interactive AI emergency dispatch system that processes real phone calls in real-time using a multi-agent architecture. Built with AWS Bedrock, LangGraph, and Retell AI to demonstrate enterprise-grade performance, robustness, and cost efficiency.

---

##  What It Does

Emergentica is a **live emergency dispatch AI** that:

1. ** Answers Real Calls** - Receives actual phone calls via Twilio/Retell AI
2. ** Transcribes in Real-Time** - Converts speech to text with <1s latency
3. ** Analyzes with Multi-Agent System** - Routes through specialized AI agents (Router → Triage → Info)
4. ** Displays Live Dashboard** - Shows classification, emotion analysis, location mapping, and dispatch recommendations
5. ** Optimizes Cost** - Achieves 67% cost reduction vs. single-model baseline while maintaining 96% accuracy

---

##  Key Features

###  Performance & Robustness (Track A)
- **96% Routing Accuracy** across 50+ test scenarios
- **<3s End-to-End Response Time** (avg. 1.59s)
- **67% Cost Reduction** through intelligent agent routing
- **98.5% Critical Emergency Detection** rate

###  Multi-Agent Architecture
```
 Incoming Call
    ↓
 Router Agent (Claude Haiku) - Fast Classification (~850ms)
    ↓
    ├─→  CRITICAL → Triage Agent (Claude Haiku) - Deep Analysis (~2.3s)
    ├─→  STANDARD → Info Agent (Claude Haiku) - Context Gathering
    └─→  NON-EMERGENCY → Info Agent (Claude Haiku) - Basic Info
```

### 🎛️ Live Dashboard
- **Real-time transcript** with caller/dispatcher color coding
- **Emotion analysis** with intensity visualization
- **Severity classification** (Critical/Standard/Non-Emergency)
- **Interactive map** with geocoded incident location
- **Dispatch recommendations** and unit status
- **Track A Performance Metrics** - Benchmark tab with accuracy, latency, and cost analysis

### 🔧 Technical Stack
- **Agents**: LangGraph orchestration with AWS Bedrock (Claude 3.5 Haiku)
- **Voice**: Retell AI Web SDK + WebSocket real-time streaming
- **Backend**: FastAPI with async WebSocket handling
- **Frontend**: HTML/Tailwind CSS with Leaflet maps
- **Observability**: LangSmith tracing for all agent interactions
- **Geocoding**: geocode.maps.co API for location services

---

##  Quick Start

### Option 1: One-Command Launch (Recommended)

```powershell
# Windows
.\start_voice_test.bat
```

```bash
# Linux/Mac
python start_voice_test.py
```

This starts:
- FastAPI backend on `localhost:8000`
- Dashboard at `http://localhost:8000/dashboard`
- Ngrok tunnel for Retell webhook
- Opens voice interface

### Option 2: Manual Setup

####  Prerequisites

```bash
# Required
- Python 3.11+
- Git

# API Keys Needed
- AWS Bedrock access (via Holistic AI proxy)
- Retell AI account (for voice)
- LangSmith API key (for observability)
- Geocoding API key (geocode.maps.co)
```

####  Installation

```bash
# Clone repository
git clone https://github.com/MuhammadMaazA/emergentica.git
cd emergentica

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

#### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys:
# - BEDROCK_API_KEY (from Holistic AI)
# - RETELL_API_KEY
# - LANGSMITH_API_KEY
# - GEOCODE_API_KEY
```

####  Run

```bash
# Terminal 1: Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Expose with ngrok
ngrok http 8000

# Terminal 3: Open dashboard
start http://localhost:8000/dashboard

# Browser: Open voice interface
open voice.html
```

####  Configure Retell (One-Time Setup)

1. Go to [Retell AI Dashboard](https://beta.retellai.com)
2. Create Custom LLM agent:
   - **WebSocket URL**: `wss://YOUR-NGROK-URL/llm-websocket/{call_id}`
   - **Voice**: `eleven_labs_adriana`
   - **Responsiveness**: 1 (max speed)
   - **Interruption Sensitivity**: 0.9
3. Copy Agent ID to `.env` as `RETELL_AGENT_ID`

---

##  Track A: Performance Metrics

Our system demonstrates **Iron Man** level performance:

| Metric | Target | Achieved | Evidence |
|--------|--------|----------|----------|
| **Routing Accuracy** | >90% | **96.0%** | [benchmark.py](benchmark.py) |
| **Response Latency** | <3s | **1.59s avg** | Real-time traces in LangSmith |
| **Critical Detection** | >95% | **98.5%** | 50+ test scenarios |
| **Cost Efficiency** | Baseline | **67% reduction** | vs. Claude Sonnet-only |
| **Robustness** | No failures | **0 crashes** | 100+ test calls |

**View Live Metrics**: Dashboard → "📊 TRACK A PERFORMANCE" tab

---

##  Architecture

### System Flow

```

┌─────────────────┐
│  Retell AI      │
│  (Voice → Text) │
└────────┬────────┘
         │ WebSocket
         ▼
┌─────────────────────────────────────┐
│       FastAPI Backend               │
│  /llm-websocket/{call_id}           │
└───────────┬─────────────────────────┘
            │
            ▼
┌───────────────────────────────────┐
│    LangGraph Orchestrator         │
│                                   │
│  ┌─────────────────────────────┐  │
│  │  Router Agent (Haiku)       │  │ ← Fast classification
│  └─────────┬───────────────────┘  │
│            │                      │
│     ┌──────┴──────┐               │
│     ▼             ▼               │
│  ┌────────┐  ┌─────────┐          │
│  │ Triage │  │  Info   │          │
│  │ (Haiku)│  │ (Haiku) │          │
│  └────────┘  └─────────┘          │
└───────────┬───────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│    Response + Dashboard Data    │
│  - Transcript                   │
│  - Severity classification      │
│  - Emotion analysis             │
│  - Location (geocoded)          │
│  - Dispatch recommendations     │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│  Dashboard (Tailwind + Leaflet) │
│                                 │
└─────────────────────────────────┘
```

### Agent Details

| Agent | Model | Purpose | Avg Latency | When Used |
|-------|-------|---------|-------------|-----------|
| **Router** | Claude 3.5 Haiku | Fast severity classification | 847ms | Every call |
| **Triage** | Claude 3.5 Haiku | Critical incident analysis + emotion | 2.3s | CRITICAL only |
| **Info** | Claude 3.5 Haiku | Standard info gathering | 1.2s | STANDARD/NON-EMERGENCY |

### Cost Optimization

```
Traditional (Sonnet for everything): $0.128 per 50 calls
Emergentica (Smart routing):        $0.042 per 50 calls
                                     ─────────────────────
Savings:                             67.3% reduction
```

---

##  Project Structure

```
emergentica/
├──  README.md                    # This file
├──  requirements.txt             # Python dependencies
├──  .env.example                 # Environment template
├──  .env                         # Your API keys (gitignored)
│
├──  agents/
│   ├── orchestrator.py             # LangGraph state machine
│   ├── router_agent.py             # Fast classification (Haiku)
│   ├── triage_agent.py             # Critical analysis (Haiku)
│   └── info_agent.py               # Info gathering (Haiku)
│
├──  Backend
│   ├── main.py                     # FastAPI + WebSocket server
│   ├── config.py                   # Configuration loader
│   ├── schemas.py                  # Pydantic data models
│   └── tools.py                    # Custom tools (geocoding)
│
├──  Frontend
│   ├── voice.html                  # Voice interface (Retell SDK)
│   └── dispatch_dashboard.html     # Emergency dispatch UI
│
├──  Evaluation
│   ├── benchmark.py                # Performance evaluation
│   └── test_helper.py              # Testing utilities
│
├──  Data
│   └── data/
│       ├── calls_master_labeled.jsonl  # Training dataset
│       └── latest_call.json            # Live call data
│
└──  Scripts
    ├── start_voice_test.bat        # Windows launcher
    └── start_voice_test.py         # Cross-platform setup
```

---

##  Usage Examples

### Making a Test Call

1. **Dial**: `+44 7493 790833`
2. **Say**: "There's a fire at UCL East, Marshgate Lane. I'm trapped on the 3rd floor!"
3. **Watch**: Dashboard updates in real-time with:
   - Transcript
   - Severity: `CRITICAL_EMERGENCY`
   - Emotion: `PANIC` (High intensity)
   - Location: Map marker on UCL East
   - Dispatch: "Fire brigade + ambulance dispatched"

### Running Benchmarks

```bash
# Test on 50 labeled scenarios
python benchmark.py

# Results saved to: data/benchmark_results.json
# View in dashboard: "Track A Performance" tab
```

### Viewing Traces

1. Go to [LangSmith](https://smith.langchain.com)
2. Select project: `emergentica-hackathon`
3. See every agent decision with full context

---

##  API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/llm-websocket/{call_id}` | WebSocket | Retell AI voice stream |
| `/api/latest-call` | GET | Latest call data for dashboard |
| `/api/benchmark` | GET | Performance metrics (Track A) |
| `/api/config` | GET | Public config (API keys for frontend) |
| `/dashboard` | GET | Serve HTML dashboard |
| `/health` | GET | Service health check |

---

##  Testing

```bash
# Unit tests
pytest tests/

# Integration test with mock call
python test_helper.py --test-orchestrator

# Load test
python benchmark.py --num-calls 100

# WebSocket test
open test_websocket.html
```

---

##  Environment Variables

```bash
# AWS Bedrock (via Holistic AI)
BEDROCK_API_KEY=your_holistic_ai_key
BEDROCK_ENDPOINT=https://api.holisticai.com/v1

# Retell AI (Voice)
RETELL_API_KEY=key_xxx
RETELL_AGENT_ID=agent_xxx

# LangSmith (Observability)
LANGSMITH_API_KEY=lsv2_pt_xxx
LANGSMITH_PROJECT=emergentica-hackathon
LANGSMITH_TRACING=true

# Geocoding
GEOCODE_API_KEY=your_geocode_key
```

---

##  Built With

- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - Claude LLMs via Holistic AI
- [Retell AI](https://retellai.com) - Voice-to-text transcription
- [FastAPI](https://fastapi.tiangolo.com/) - Async WebSocket backend
- [Pydantic](https://pydantic.dev/) - Data validation
- [LangSmith](https://smith.langchain.com/) - Observability & tracing
- [Leaflet](https://leafletjs.com/) - Interactive maps
- [Tailwind CSS](https://tailwindcss.com/) - Dashboard styling


---

##  License

MIT License - See [LICENSE](LICENSE) for details

---

##  Acknowledgments

- **Holistic AI** for AWS Bedrock access
- **UCL** for hosting The Great Agent Hack 2025
- **Retell AI** for voice infrastructure
- **LangChain** for LangGraph framework

---

<div align="center">

** Built for The Great Agent Hack 2025 **

*Demonstrating enterprise-grade AI with real-time voice, multi-agent intelligence, and production-ready performance*

</div>
