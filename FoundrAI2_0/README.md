# FoundrAI 2.0 🤖🏛️

> **A Deliberative, Consensus-Driven Multi-Agent AI Startup Simulator**

FoundrAI 2.0 upgrades the classic single-pass AI pipeline into a **round-table of specialized AI agents** that debate, critique, revise, and converge on a validated business plan — then export it as a polished **PDF**.

![FoundrAI 2.0 Architecture](https://img.shields.io/badge/Architecture-Multi--Agent%20Deliberative-6366f1?style=for-the-badge)
![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20Docker-3b82f6?style=for-the-badge)
![Model](https://img.shields.io/badge/AI-Qwen2.5%20via%20HuggingFace-10b981?style=for-the-badge)

---

## ✨ What Makes This Different

| Feature | FoundrAI 1.0 | **FoundrAI 2.0** |
|---|---|---|
| Agent execution | Sequential pipeline | **Parallel + iterative** |
| Agent behavior | Generate output | **Generate → Critique → Revise** |
| Consensus | None | **Scored feedback loop (target 7.5/10)** |
| Output | Text cards | **Structured business plan + PDF** |
| UI | Agent cards | **Live round-table with chat feed** |
| API calls | Fixed | **Fast mode (~6) / Deep mode (~14)** |

---

## 🏛️ System Architecture

```
User Idea
    │
    ▼
┌──────────────────────────────────────┐
│  Phase 1 · CEO Proposal              │  Primary agent drafts the initial vision
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│  Phase 2 · Parallel Critique (all specialists simultaneously) │
│  ┌───────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐  │
│  │ Developer │  │ Finance  │  │ Marketing │  │  Risk    │  │
│  │ Feasible? │  │ Viable?  │  │ Traction? │  │ Safe?    │  │
│  │ [score]   │  │ [score]  │  │ [score]   │  │ [score]  │  │
│  └───────────┘  └──────────┘  └───────────┘  └──────────┘  │
└──────────────────────────────────────────────────────────────┘
    │
    ▼  ← iterates until avg score ≥ 7.5 or max rounds
┌──────────────────────────────────────┐
│  Phase 3 · Revision & Negotiation    │  CEO revises; agents re-score
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────┐
│  Phase 4 · Synthesis                 │  Chief Strategist produces final plan
└──────────────────────────────────────┘
    │
    ▼
┌─────────────────────┐
│  PDF Business Plan  │  Downloadable, styled with reportlab
└─────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A [Hugging Face](https://huggingface.co) account with an API token

### 1. Clone & Configure

```bash
git clone <your-repo-url>
cd FoundrAI2_0
```

Edit `backend/.env` and set your HuggingFace token:
```env
HF_TOKEN=hf_your_token_here
```

### 2. Launch with Docker

```bash
docker compose up -d --build
```

This builds and starts:
- **Backend** → `http://localhost:8000` (FastAPI + Uvicorn)
- **Frontend** → `http://localhost:5173` (React via Nginx)

### 3. Open the App

Navigate to **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 🎮 How to Use

1. **Type your startup idea** in the text area
2. **Choose a mode:**
   - ⚡ **Fast Mode** — ~6 API calls, results in ~20-30 seconds (CEO + Dev + Finance)
   - 🧠 **Deep Mode** — up to 14 API calls, all 5 agents + 2 revision rounds
3. **Click Launch** — watch the AI round table come alive:
   - Phase indicator shows current stage
   - Live chat feed streams agent discussion
   - Consensus meter rises as agents align
4. **Explore the Business Plan** using the section tabs
5. **Download the PDF** once consensus is reached

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | REST API + Server-Sent Events (SSE) streaming |
| **`huggingface_hub`** | InferenceClient for AI model calls |
| **Qwen/Qwen2.5-72B-Instruct** | Primary LLM (Deep mode) |
| **Qwen/Qwen2.5-7B-Instruct** | Fast mode LLM |
| **reportlab** | PDF generation |
| **asyncio.gather** | Parallel agent execution |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** | UI framework |
| **Vite** | Build tool |
| **Lucide React** | Icons |
| **Vanilla CSS** | Styling (glassmorphism, animations) |
| **Server-Sent Events** | Real-time streaming from backend |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker + Docker Compose** | Containerization |
| **Nginx** | Serving the built React app |

---

## 📂 Project Structure

```
FoundrAI2_0/
├── backend/
│   ├── agents.py          # Agent propose/critique/revise/synthesize logic
│   ├── orchestrator.py    # 4-phase SSE streaming pipeline
│   ├── pdf_generator.py   # reportlab PDF export
│   ├── main.py            # FastAPI app: /simulate, /download-report, /health
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env               # HF_TOKEN goes here
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Round-table UI with chat feed, consensus meter, plan tabs
│   │   ├── index.css      # Full design system: glassmorphism, animations, layout
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔌 API Reference

### `POST /simulate`
Start a simulation. Returns a **Server-Sent Events** stream.

**Request body:**
```json
{
  "idea": "An AI-powered app that generates personalized diets based on blood tests",
  "fast": true
}
```

**SSE Event types emitted:**
| Type | Description |
|---|---|
| `system_start` | Simulation begins |
| `phase_change` | Phase transition (1-4) |
| `agent_thinking` | Agent is computing |
| `proposal` | CEO initial proposal |
| `critique` | Agent critique + score |
| `revision` | CEO revised proposal |
| `re_score` | Agent re-evaluation |
| `consensus_update` | Average score update |
| `consensus_reached` | Convergence achieved |
| `final_plan` | Structured business plan |
| `pdf_ready` | PDF available for download |
| `system_done` | Simulation complete |

### `GET /download-report`
Download the generated PDF business plan.

### `GET /health`
Health check: `{"status": "ok", "service": "FoundrAI 2.0"}`

---

## 🎨 UI Features

- **Pentagon agent layout** — agents arranged in a round-table with a live consensus score in the center
- **Live chat bubbles** — each event appears as a real-time message with agent color coding
- **Consensus meter** — animated progress bar with 7.5/10 threshold marker
- **Convergence banner** — green confirmation when all agents align
- **Tabbed business plan** — 5 clickable sections (Exec Summary, Tech Stack, Finance, Marketing, Risk)
- **PDF download button** — appears on convergence, fetches from `/download-report`
- **Fast/Deep mode toggle** — switch between speed and depth before launching

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `HF_TOKEN` | ✅ | Hugging Face API token (from [hf.co/settings/tokens](https://huggingface.co/settings/tokens)) |

---

## 📜 License

MIT License — feel free to fork, modify, and build upon this.

---

## 🙌 Acknowledgements

Built for the **Hack2Skills Hackathon** — demonstrating deliberative multi-agent AI systems using open-source LLMs and modern web tooling.
