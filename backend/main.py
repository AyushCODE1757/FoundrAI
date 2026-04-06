import asyncio
import json
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel

from orchestrator import run_simulation_stream

app = FastAPI(title="FoundrAI 2.0 — Deliberative Multi-Agent System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Models ────────────────────────────────────────────────────────────

class IdeaRequest(BaseModel):
    idea: str
    fast: bool = False

class DeployRequest(BaseModel):
    idea: str
    plan: dict          # final synthesized plan sections

class MonitorRequest(BaseModel):
    idea: str


# ── Simulate ──────────────────────────────────────────────────────────────────

@app.post("/simulate")
async def simulate(request: IdeaRequest):
    return StreamingResponse(
        run_simulation_stream(request.idea, request.fast),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Approve & Deploy to GitHub ────────────────────────────────────────────────

@app.post("/approve-deploy")
async def approve_deploy(request: DeployRequest):
    """
    Human-in-the-loop approval gate.
    After user clicks Approve in the UI, this endpoint:
    1. Generates boilerplate codebase files via LLM
    2. Deploys to a new private GitHub repo
    3. Returns the repo URL
    """
    from agents import generate_boilerplate
    from tools import deploy_to_github

    # Step 1: Generate boilerplate files (LLM call)
    files = await asyncio.to_thread(generate_boilerplate, request.idea, request.plan)

    # Step 2: Create repo name from idea
    repo_name = "-".join(request.idea.lower().split()[:4]) + "-foundrai"

    # Step 3: Deploy to GitHub
    repo_url = deploy_to_github.invoke({
        "repo_name": repo_name,
        "files_json": json.dumps(files),
    })

    return {
        "repo_url": repo_url,
        "files_generated": list(files.keys()),
        "repo_name": repo_name,
    }


# ── Auto-Monitor (Fast-Forward Demo) ─────────────────────────────────────────

@app.post("/monitor")
async def monitor(request: MonitorRequest):
    """
    Simulates the auto-monitor daemon waking up.
    Fetches fresh market data and returns an updated strategy as SSE stream.
    """
    from tools import search_recent_startups, search_competitors
    from agents import generate_monitor_update

    def _stream():
        def sse(data):
            return f"data: {json.dumps(data)}\n\n"

        yield sse({"type": "monitor_start", "idea": request.idea})
        yield sse({"type": "monitor_scanning", "message": f"🔍 Scanning market for '{request.idea}'…"})

        # Fetch fresh Tavily data
        scan_query  = f"{request.idea} new competitor launch 2025"
        fresh_data  = search_recent_startups.invoke(scan_query)
        comp_data   = search_competitors.invoke(request.idea)
        combined    = f"[Latest News]\n{fresh_data}\n\n[Competitor Update]\n{comp_data}"

        yield sse({
            "type": "monitor_data",
            "message": "📡 New market signals detected",
            "snippet": (fresh_data[:200] + "...") if len(fresh_data) > 200 else fresh_data,
        })

        # Generate updated strategy
        yield sse({"type": "monitor_updating", "message": "⚡ Auto-revising strategy…"})
        updated_strategy = generate_monitor_update(request.idea, combined)

        yield sse({
            "type": "monitor_done",
            "updated_section": "Marketing Strategy",
            "updated_content": updated_strategy,
        })

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Download PDF ──────────────────────────────────────────────────────────────

@app.get("/download-report")
async def download_report():
    path = "/tmp/foundrai_report.pdf"
    if not os.path.exists(path):
        return {"error": "No report available. Run a simulation first."}
    return FileResponse(path, media_type="application/pdf", filename="FoundrAI_Business_Plan.pdf")


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "FoundrAI 2.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
