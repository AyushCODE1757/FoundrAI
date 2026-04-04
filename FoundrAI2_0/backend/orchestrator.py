"""
FoundrAI 2.0 — Orchestrator
4-Phase deliberative pipeline with tool-use SSE events.

Event order per agent:
  tool_call   → agent is querying an external API
  tool_result → snippet of what the tool returned
  proposal / critique / revision → LLM synthesis grounded in real data
"""

import asyncio
import json
from agents import (
    ceo_propose, dev_critique, finance_critique,
    marketing_critique, risk_critique, ceo_revise, synthesize
)

CONSENSUS_THRESHOLD = 7.5


def sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def _emit_tool_events(result: dict, phase: int) -> list[str]:
    """Return tool_call + tool_result SSE strings if the agent used a tool."""
    events = []
    if result.get("tool_name"):
        events.append(sse({
            "type": "tool_call",
            "agent": result["agent"],
            "tool": result["tool_name"],
            "query": result.get("tool_query", ""),
            "phase": phase,
        }))
        events.append(sse({
            "type": "tool_result",
            "agent": result["agent"],
            "tool": result["tool_name"],
            "snippet": result.get("tool_result_snippet", ""),
            "phase": phase,
        }))
    return events


async def run_simulation_stream(idea: str, fast: bool = False):
    """
    Fast mode  (~8 calls):  1 proposal + 2 critiques + 1 revision + 1 synthesis
                            + 3 tool calls (Tavily×1, GitHub×1, Trends×1)
    Normal mode (~16 calls): 1 proposal + 4 critiques + 1 revision + re-score + 1 synthesis
                             + 5 tool calls (all agents)
    """

    # ── SYSTEM START ─────────────────────────────────────────────────────────
    yield sse({"type": "system_start", "fast_mode": fast})

    # ── PHASE 1: CEO PROPOSAL ────────────────────────────────────────────────
    yield sse({"type": "phase_change", "phase": 1, "label": "CEO Proposal"})
    yield sse({"type": "agent_thinking", "agent": "CEO", "phase": 1})

    ceo_result = await asyncio.to_thread(ceo_propose, idea, fast)

    # Stream tool events first
    for event in _emit_tool_events(ceo_result, 1):
        yield event

    proposal = ceo_result["content"]
    yield sse({
        "type": "proposal", "agent": "CEO", "phase": 1,
        "content": proposal,
        "grounded_by": ceo_result.get("tool_name"),
    })

    # ── PHASE 2: PARALLEL CRITIQUE ───────────────────────────────────────────
    yield sse({"type": "phase_change", "phase": 2, "label": "Parallel Critique"})

    if fast:
        critic_agents = ["Developer", "Finance"]
        critique_fns = [
            asyncio.to_thread(dev_critique, idea, proposal, True),
            asyncio.to_thread(finance_critique, idea, proposal, True),
        ]
    else:
        critic_agents = ["Developer", "Finance", "Marketing", "Risk"]
        critique_fns = [
            asyncio.to_thread(dev_critique, idea, proposal, False),
            asyncio.to_thread(finance_critique, idea, proposal, False),
            asyncio.to_thread(marketing_critique, idea, proposal, False),
            asyncio.to_thread(risk_critique, idea, proposal, False),
        ]

    for agent in critic_agents:
        yield sse({"type": "agent_thinking", "agent": agent, "phase": 2})

    critique_results = await asyncio.gather(*critique_fns)
    all_critiques = list(critique_results)

    # Emit tool events then critique for each agent
    for c in all_critiques:
        for event in _emit_tool_events(c, 2):
            yield event
        yield sse({
            "type": "critique", "agent": c["agent"], "phase": 2,
            "content": c["content"], "score": c["score"],
            "grounded_by": c.get("tool_name"),
        })

    avg_score = sum(c["score"] for c in all_critiques) / len(all_critiques)
    yield sse({"type": "consensus_update", "score": round(avg_score, 1), "round": 0})

    # ── PHASE 3: ITERATIVE REVISION LOOP ────────────────────────────────────
    yield sse({"type": "phase_change", "phase": 3, "label": "Negotiation & Revision"})

    current_proposal = proposal
    max_rounds = 1 if fast else 2

    for round_num in range(1, max_rounds + 1):
        if avg_score >= CONSENSUS_THRESHOLD:
            break

        yield sse({"type": "agent_thinking", "agent": "CEO", "phase": 3})
        revised_result = await asyncio.to_thread(
            ceo_revise, idea, current_proposal, all_critiques, round_num, fast
        )
        current_proposal = revised_result["content"]
        yield sse({
            "type": "revision", "agent": "CEO", "phase": 3,
            "content": current_proposal, "round": round_num,
        })

        if fast or round_num == max_rounds:
            break

        # Re-score in normal mode (Dev + Finance only to stay under call budget)
        rescore_fns = [
            asyncio.to_thread(dev_critique, idea, current_proposal, False),
            asyncio.to_thread(finance_critique, idea, current_proposal, False),
        ]
        for a in ["Developer", "Finance"]:
            yield sse({"type": "agent_thinking", "agent": a, "phase": 3})

        new_scores = await asyncio.gather(*rescore_fns)
        for s in new_scores:
            for event in _emit_tool_events(s, 3):
                yield event
            yield sse({
                "type": "re_score", "agent": s["agent"], "phase": 3,
                "content": s["content"], "score": s["score"],
            })

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
