# Emergentica - Live Voice-Interactive Agentic System

**Track A: Iron Man (Performance & Robustness)**

A live, voice-interactive AI dispatcher system that answers real phone calls, transcribes speech in real-time, uses a multi-agent backend built on AWS Bedrock and LangGraph to analyze call severity and emotional context, and presents a fully-reasoned, actionable report on a Streamlit dispatcher dashboard.

## 🏆 Key Features

- **Live Voice Interaction**: Real phone calls via Twilio + Retell AI
- **Multi-Agent Architecture**: LangGraph-powered workflow with specialized agents
- **Real-time Analysis**: Severity classification, emotion analysis, and incident reporting
- **Smart Routing**: Cost-optimized agent routing (Haiku → Sonnet → Llama)
- **Live Dashboard**: Streamlit-based dispatcher interface
- **Benchmarked Performance**: Data-backed metrics for routing accuracy and cost efficiency

## 🏗️ Architecture

### Agent Workflow
```
RouterAgent (Haiku) → Severity Classification
    ↓
    ├─→ CRITICAL_EMERGENCY → TriageAgent (Sonnet) → Full Analysis
    ├─→ STANDARD_ASSISTANCE → InfoAgent (Llama) → Basic Info
    └─→ NON_EMERGENCY → InfoAgent (Llama) → Basic Info
```

### Components
- **RouterAgent**: Fast, cost-efficient severity classification
- **TriageAgent**: Deep analysis with emotion detection for critical calls
- **InfoAgent**: Information gathering and context enrichment
- **Voice Pipeline**: Twilio + Retell AI for real-time transcription
- **Dashboard**: Live Streamlit interface for dispatchers

## 🚀 Quick Start

### 📞 **NEW! Live Voice Testing** 

Test with **real phone calls** and **voice AI responses**:

**👉 Start Here:** [TESTING_README.md](TESTING_README.md)

**Quick Options:**
- 🚀 One-click: `.\start_voice_test.bat`
- 🐍 Setup helper: `py start_voice_test.py`
- 📖 5-min guide: [QUICK_START_VOICE.md](QUICK_START_VOICE.md)
- 📊 Flow diagram: [VOICE_FLOW_DIAGRAM.md](VOICE_FLOW_DIAGRAM.md)
- 🎨 Visual guide: [VISUAL_GUIDE.txt](VISUAL_GUIDE.txt)

**Test Number:** `+44 7493 790833`

### 🖥️ Standard Setup (No Voice)

### Prerequisites
- Python 3.11+
- Twilio account (phone number)
- Retell AI account (voice agent)
- LangSmith account (observability)
- Geocoding API key

### Installation

1. **Clone and setup**:
```bash
cd dispatch_ai
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Prepare data** (Phase 0.2):
```bash
python scripts/preprocess_data.py
```

## 📊 Project Phases

### ✅ Phase 0: Foundation
- [x] 0.1: Project initialization & API configuration
- [ ] 0.2: Dataset curation & AI-powered labeling

### Phase 1: Agentic Brain (Workstream A)
- [ ] 1.1: Schemas and tools (`schemas.py`, `tools.py`)
- [ ] 1.2: LangGraph workflow (`orchestrator.py`)

### Phase 2: Live Interface (Workstream B)
- [ ] 2.1: Telephony & voice endpoint (`main.py`)
- [ ] 2.2: Dashboard UI (`dashboard.py`)

### Phase 3: Integration
- [ ] 3.1: Full system integration

### Phase 4: Benchmarking
- [ ] 4.1: Performance & robustness report (`benchmark.py`)

## 📁 Project Structure

```
dispatch_ai/
├── .env                    # API keys and configuration
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── agents/
│   ├── orchestrator.py    # LangGraph state machine
│   ├── router_agent.py    # RouterAgent (Haiku)
│   ├── triage_agent.py    # TriageAgent (Sonnet)
│   └── info_agent.py      # InfoAgent (Llama)
├── schemas.py             # Pydantic schemas
├── tools.py               # Custom tools (geocoding, search)
├── main.py                # FastAPI server for voice
├── dashboard.py           # Streamlit dispatcher UI
├── scripts/
│   └── preprocess_data.py # Data labeling script
├── benchmark.py           # Performance evaluation
└── data/
    ├── calls_master_labeled.jsonl  # Labeled dataset
    └── latest_call.json            # Live call data
```

## 🎯 Key Metrics (Track A)

Our system will be benchmarked on:

1. **Routing Accuracy**: % of calls correctly classified
2. **Average Routing Latency**: Time to classify calls
3. **Average Critical Triage Time**: End-to-end time for critical calls
4. **Cost-Efficiency**: Savings vs. using Sonnet for all calls

## 🔧 Technologies

- **Agentic Core**: LangGraph, AWS Bedrock (via Holistic AI Proxy), Pydantic, LangSmith
- **Voice & Telephony**: Twilio, Retell AI, FastAPI
- **Frontend**: Streamlit
- **Models**: Claude Haiku, Claude Sonnet, Llama (via AWS Bedrock)

## 📝 Development Workflow

### Running the System

1. **Start the voice server**:
```bash
python main.py
```

2. **Start the dashboard**:
```bash
streamlit run dashboard.py
```

3. **Call the Twilio number** and watch the dashboard update in real-time!

### Running Benchmarks

```bash
python benchmark.py
```

## 🏅 Hackathon Compliance

- ✅ Uses AWS Bedrock via Holistic AI Proxy
- ✅ Built with LangGraph for agentic workflows
- ✅ Implements Pydantic for structured outputs
- ✅ Instrumented with LangSmith for observability
- ✅ Focuses on Performance & Robustness (Track A)

## 📄 License

MIT License - Built for The Great Agent Hack 2025

---

**Team**: [Your Team Name]
**Track**: A - Iron Man (Performance & Robustness)
**Hackathon**: The Great Agent Hack 2025 - Holistic AI x UCL
