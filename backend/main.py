# import asyncio
# import json
# import os

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import StreamingResponse, FileResponse
# from pydantic import BaseModel

# from orchestrator import run_simulation_stream

# app = FastAPI(title="FoundrAI 2.0 — Deliberative Multi-Agent System")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ── Request Models ────────────────────────────────────────────────────────────

# class IdeaRequest(BaseModel):
#     idea: str
#     fast: bool = False

# class DeployRequest(BaseModel):
#     idea: str
#     plan: dict          # final synthesized plan sections
#     repo_name: str | None = None  # Add this field

# class MonitorRequest(BaseModel):
#     idea: str


# # ── Simulate ──────────────────────────────────────────────────────────────────

# @app.post("/simulate")
# async def simulate(request: IdeaRequest):
#     return StreamingResponse(
#         run_simulation_stream(request.idea, request.fast),
#         media_type="text/event-stream",
#         headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
#     )


# # ── Approve & Deploy to GitHub ────────────────────────────────────────────────

# @app.post("/approve-deploy")
# async def approve_deploy(request: DeployRequest):
#     """
#     Human-in-the-loop approval gate.
#     After user clicks Approve in the UI, this endpoint:
#     1. Generates boilerplate codebase files via LLM
#     2. Deploys to a new private GitHub repo
#     3. Returns the repo URL
#     """
#     from agents import generate_boilerplate
#     from tools import deploy_to_github

#     # Step 1: Generate boilerplate files (LLM call)
#     files = await asyncio.to_thread(generate_boilerplate, request.idea, request.plan)

#     # Step 2: Create repo name from idea
#     # Use the user's name, or fallback to the auto-generated one if they leave it blank
#     if request.repo_name and request.repo_name.strip():
#         # Sanitize to ensure it's a valid GitHub repo name (no spaces)
#         repo_name = request.repo_name.strip().replace(" ", "-").lower()
#     else:
#         repo_name = "-".join(request.idea.lower().split()[:4]) + "-foundrai"

#     # Step 3: Deploy to GitHub
#     repo_url = deploy_to_github.invoke({
#         "repo_name": repo_name,
#         "files_json": json.dumps(files),
#     })

#     return {
#         "repo_url": repo_url,
#         "files_generated": list(files.keys()),
#         "repo_name": repo_name,
#     }


# # ── Auto-Monitor (Fast-Forward Demo) ─────────────────────────────────────────

# @app.post("/monitor")
# async def monitor(request: MonitorRequest):
#     """
#     Simulates the auto-monitor daemon waking up.
#     Fetches fresh market data and returns an updated strategy as SSE stream.
#     """
#     from tools import search_recent_startups, search_competitors
#     from agents import generate_monitor_update

#     def _stream():
#         def sse(data):
#             return f"data: {json.dumps(data)}\n\n"

#         yield sse({"type": "monitor_start", "idea": request.idea})
#         yield sse({"type": "monitor_scanning", "message": f"🔍 Scanning market for '{request.idea}'…"})

#         # Fetch fresh Tavily data
#         scan_query  = f"{request.idea} new competitor launch 2025"
#         fresh_data  = search_recent_startups.invoke(scan_query)
#         comp_data   = search_competitors.invoke(request.idea)
#         combined    = f"[Latest News]\n{fresh_data}\n\n[Competitor Update]\n{comp_data}"

#         yield sse({
#             "type": "monitor_data",
#             "message": "📡 New market signals detected",
#             "snippet": (fresh_data[:200] + "...") if len(fresh_data) > 200 else fresh_data,
#         })

#         # Generate updated strategy
#         yield sse({"type": "monitor_updating", "message": "⚡ Auto-revising strategy…"})
#         updated_strategy = generate_monitor_update(request.idea, combined)

#         yield sse({
#             "type": "monitor_done",
#             "updated_section": "Marketing Strategy",
#             "updated_content": updated_strategy,
#         })

#     return StreamingResponse(
#         _stream(),
#         media_type="text/event-stream",
#         headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
#     )


# # ── Download PDF ──────────────────────────────────────────────────────────────

# @app.get("/download-report")
# async def download_report():
#     path = "/tmp/foundrai_report.pdf"
#     if not os.path.exists(path):
#         return {"error": "No report available. Run a simulation first."}
#     return FileResponse(path, media_type="application/pdf", filename="FoundrAI_Business_Plan.pdf")


# # ── Health ────────────────────────────────────────────────────────────────────

# @app.get("/health")
# async def health():
#     return {"status": "ok", "service": "FoundrAI 2.0"}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


import asyncio
import json
import os
import re

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


# ── Request Models ─────────────────────────────────────────────────────────────

class IdeaRequest(BaseModel):
    idea: str
    fast: bool = False


class DeployRequest(BaseModel):
    idea: str
    plan: dict          # final synthesized plan sections
    repo_name: str | None = None   # user-chosen name from the modal input


class MonitorRequest(BaseModel):
    idea: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def sanitise_repo_name(raw: str) -> str:
    """GitHub repo name rules: lowercase, letters/digits/hyphens, no leading hyphen."""
    name = raw.strip().lower()
    name = re.sub(r"[^a-z0-9\-]", "-", name)   # replace invalid chars with -
    name = re.sub(r"-+", "-", name)              # collapse consecutive hyphens
    name = name.strip("-")                        # strip leading/trailing hyphens
    return name or "foundrai-project"


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

    Flow:
      1. User fills repo name in the modal and clicks "Create Project & Push Code"
      2. Frontend POST /approve-deploy  { idea, plan, repo_name }
      3. This endpoint:
            a. Sanitises the repo name
            b. Generates boilerplate files via LLM
            c. Creates a private GitHub repo via PyGithub
            d. Pushes files to main branch
            e. Returns { repo_url, repo_name, files_generated }

    Required env vars:
        GITHUB_TOKEN   — personal access token with repo scope
        GITHUB_ORG     — organisation slug  (or leave blank to use authenticated user)

    Install:
        pip install PyGithub
    """
    from agents import generate_boilerplate
    from tools import deploy_to_github

    # ── 1. Decide final repo name ─────────────────────────────────────────────
    if request.repo_name and request.repo_name.strip():
        repo_name = sanitise_repo_name(request.repo_name)
    else:
        # Auto-derive from idea text
        repo_name = sanitise_repo_name(
            "-".join(request.idea.lower().split()[:4]) + "-foundrai"
        )

    # ── 2. Generate boilerplate files (LLM call) ──────────────────────────────
    # generate_boilerplate should return a dict:
    #   { "README.md": "...", "docker-compose.yml": "...", ... }
    files: dict = await asyncio.to_thread(
        generate_boilerplate, request.idea, request.plan
    )

    # ── 3. Push to GitHub ─────────────────────────────────────────────────────
    # deploy_to_github.invoke expects:
    #   { "repo_name": str, "files_json": str (JSON of files dict) }
    # and returns the HTML URL of the new repo.
    repo_url: str = deploy_to_github.invoke({
        "repo_name": repo_name,
        "files_json": json.dumps(files),
    })

    return {
        "repo_url":        repo_url,
        "repo_name":       repo_name,
        "files_generated": list(files.keys()),
    }


# ── Auto-Monitor (Fast-Forward Demo) ─────────────────────────────────────────

@app.post("/monitor")
async def monitor(request: MonitorRequest):
    """
    Simulates the auto-monitor daemon waking up.
    Fetches fresh market data and returns an updated strategy as an SSE stream.

    Frontend trigger: the "Fast-Forward Demo" button in ResultsStage.
    """
    from tools import search_recent_startups, search_competitors
    from agents import generate_monitor_update

    def _stream():
        def sse(data: dict) -> str:
            return f"data: {json.dumps(data)}\n\n"

        yield sse({"type": "monitor_start",    "idea": request.idea})
        yield sse({"type": "monitor_scanning", "message": f"🔍 Scanning market for '{request.idea}'…"})

        # Fetch fresh Tavily / search data
        scan_query  = f"{request.idea} new competitor launch 2025"
        fresh_data  = search_recent_startups.invoke(scan_query)
        comp_data   = search_competitors.invoke(request.idea)
        combined    = f"[Latest News]\n{fresh_data}\n\n[Competitor Update]\n{comp_data}"

        yield sse({
            "type":    "monitor_data",
            "message": "📡 New market signals detected",
            "snippet": (fresh_data[:200] + "…") if len(fresh_data) > 200 else fresh_data,
        })

        yield sse({"type": "monitor_updating", "message": "⚡ Auto-revising strategy…"})

        updated_strategy = generate_monitor_update(request.idea, combined)

        yield sse({
            "type":            "monitor_done",
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
    return FileResponse(
        path,
        media_type="application/pdf",
        filename="FoundrAI_Business_Plan.pdf",
    )


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "FoundrAI 2.0"}


# ── Dev entrypoint ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)