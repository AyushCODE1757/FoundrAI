import asyncio
import json
from agents import (
    ceo_propose, dev_critique, finance_critique,
    marketing_critique, risk_critique, ceo_revise, synthesize
)

CONSENSUS_THRESHOLD = 7.5

def sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"

async def run_simulation_stream(idea: str, fast: bool = False):
    """
    4-Phase deliberative consensus pipeline streamed via SSE.

    Fast mode  (~6 API calls): 1 proposal + 2 critiques + 1 revision + 1 synthesis + done
    Normal mode (~10-14 calls): 1 proposal + 4 critiques + up to 2 revision rounds + 1 synthesis
    """

    # ── SYSTEM START ─────────────────────────────────────────────────────────
    yield sse({"type": "system_start", "fast_mode": fast})

    # ── PHASE 1: CEO PROPOSAL ────────────────────────────────────────────────
    yield sse({"type": "phase_change", "phase": 1, "label": "CEO Proposal"})
    yield sse({"type": "agent_thinking", "agent": "CEO", "phase": 1})

    proposal = await asyncio.to_thread(ceo_propose, idea, fast)
    yield sse({"type": "proposal", "agent": "CEO", "phase": 1, "content": proposal})

    # ── PHASE 2: PARALLEL CRITIQUE ───────────────────────────────────────────
    yield sse({"type": "phase_change", "phase": 2, "label": "Parallel Critique"})

    if fast:
        # Fast mode: only Dev + Finance critique (2 calls)
        critic_agents = ["Developer", "Finance"]
        critique_fns = [
            asyncio.to_thread(dev_critique, idea, proposal, True),
            asyncio.to_thread(finance_critique, idea, proposal, True),
        ]
    else:
        # Normal mode: all 4 specialists critique (4 calls)
        critic_agents = ["Developer", "Finance", "Marketing", "Risk"]
        critique_fns = [
            asyncio.to_thread(dev_critique, idea, proposal, False),
            asyncio.to_thread(finance_critique, idea, proposal, False),
            asyncio.to_thread(marketing_critique, idea, proposal, False),
            asyncio.to_thread(risk_critique, idea, proposal, False),
        ]

    for agent in critic_agents:
        yield sse({"type": "agent_thinking", "agent": agent, "phase": 2})

    # Run all critiques in parallel
    critique_results = await asyncio.gather(*critique_fns)
    all_critiques = list(critique_results)

    for c in all_critiques:
        yield sse({"type": "critique", "agent": c["agent"], "phase": 2,
                   "content": c["content"], "score": c["score"]})

    avg_score = sum(c["score"] for c in all_critiques) / len(all_critiques)
    yield sse({"type": "consensus_update", "score": round(avg_score, 1), "round": 0})

    # ── PHASE 3: ITERATIVE REVISION LOOP ────────────────────────────────────
    yield sse({"type": "phase_change", "phase": 3, "label": "Negotiation & Revision"})

    current_proposal = proposal
    max_rounds = 1 if fast else 2  # fast=1 revision, normal=up to 2

    for round_num in range(1, max_rounds + 1):
        if avg_score >= CONSENSUS_THRESHOLD:
            break

        # CEO revises
        yield sse({"type": "agent_thinking", "agent": "CEO", "phase": 3})
        revised = await asyncio.to_thread(ceo_revise, idea, current_proposal, all_critiques, round_num, fast)
        current_proposal = revised
        yield sse({"type": "revision", "agent": "CEO", "phase": 3,
                   "content": revised, "round": round_num})

        if fast or round_num == max_rounds:
            # In fast mode we skip re-scoring to save calls
            break

        # Re-score (only in normal mode, only round 1 to stay under budget)
        rescore_fns = [
            asyncio.to_thread(dev_critique, idea, revised, False),
            asyncio.to_thread(finance_critique, idea, revised, False),
        ]
        for a in ["Developer", "Finance"]:
            yield sse({"type": "agent_thinking", "agent": a, "phase": 3})

        new_scores = await asyncio.gather(*rescore_fns)
        for s in new_scores:
            yield sse({"type": "re_score", "agent": s["agent"], "phase": 3,
                       "content": s["content"], "score": s["score"]})

        avg_score = sum(s["score"] for s in new_scores) / len(new_scores)
        yield sse({"type": "consensus_update", "score": round(avg_score, 1), "round": round_num})

    yield sse({"type": "consensus_reached", "final_score": round(avg_score, 1)})

    # ── PHASE 4: SYNTHESIS ───────────────────────────────────────────────────
    yield sse({"type": "phase_change", "phase": 4, "label": "Final Synthesis"})
    yield sse({"type": "agent_thinking", "agent": "Synthesis", "phase": 4})

    plan = await asyncio.to_thread(synthesize, idea, current_proposal, all_critiques, fast)
    yield sse({"type": "final_plan", "agent": "Synthesis", "phase": 4, "plan": plan})

    # Generate PDF
    try:
        from pdf_generator import generate_pdf
        generate_pdf(idea, current_proposal, all_critiques, plan)
        yield sse({"type": "pdf_ready"})
    except Exception as e:
        yield sse({"type": "pdf_error", "error": str(e)})

    yield sse({"type": "system_done"})
