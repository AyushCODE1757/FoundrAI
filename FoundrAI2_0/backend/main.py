from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import os

from orchestrator import run_simulation_stream

app = FastAPI(title="FoundrAI 2.0 — Deliberative Multi-Agent System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IdeaRequest(BaseModel):
    idea: str
    fast: bool = False  # fast mode: ~6 API calls; normal: ~12-14

@app.post("/simulate")
async def simulate(request: IdeaRequest):
    return StreamingResponse(
        run_simulation_stream(request.idea, request.fast),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

@app.get("/download-report")
async def download_report():
    path = "/tmp/foundrai_report.pdf"
    if not os.path.exists(path):
        return {"error": "No report available. Run a simulation first."}
    return FileResponse(
        path,
        media_type="application/pdf",
        filename="FoundrAI_Business_Plan.pdf"
    )

@app.get("/health")
async def health():
    return {"status": "ok", "service": "FoundrAI 2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
