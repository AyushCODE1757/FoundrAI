import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

# Model config: fast mode uses a small, snappy model; normal uses larger
FAST_MODEL = "Qwen/Qwen2.5-7B-Instruct"
NORMAL_MODEL = "Qwen/Qwen2.5-72B-Instruct"

def get_client():
    return InferenceClient(api_key=HF_TOKEN)

def call_ai(prompt: str, fast: bool = False) -> str:
    if not HF_TOKEN:
        return f"[MOCK] No HF_TOKEN found. Prompt: {prompt[:40]}..."
    client = get_client()
    model = FAST_MODEL if fast else NORMAL_MODEL
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.75,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling AI: {str(e)}"

# ── PHASE 1: CEO Proposal ─────────────────────────────────────────────────────

def ceo_propose(idea: str, fast: bool = False) -> str:
    prompt = (
        f"You are the visionary CEO of a new startup. The idea is: '{idea}'.\n"
        "Draft a concise initial business proposal (3-4 sentences) covering:\n"
        "1. Core value proposition\n"
        "2. Target market\n"
        "3. High-level go-to-market strategy\n"
        "Be bold and specific. Do NOT use bullet points — write in prose."
    )
    return call_ai(prompt, fast)

# ── PHASE 2: Specialist Critique ─────────────────────────────────────────────

def dev_critique(idea: str, proposal: str, fast: bool = False) -> dict:
    prompt = (
        f"You are the Lead Developer reviewing this startup proposal for technical feasibility.\n"
        f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
        "Give a 2-3 sentence critique focusing on technical risks and the suggested tech stack. "
        "End your response with exactly: [SCORE: X/10] where X is your consensus score (how ready is this technically)."
    )
    raw = call_ai(prompt, fast)
    return _parse_critique(raw, "Developer")

def finance_critique(idea: str, proposal: str, fast: bool = False) -> dict:
    prompt = (
        f"You are the CFO reviewing this startup proposal for financial viability.\n"
        f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
        "Give a 2-3 sentence critique covering estimated costs and revenue model. "
        "End your response with exactly: [SCORE: X/10] where X is your consensus score (how financially sound is this)."
    )
    raw = call_ai(prompt, fast)
    return _parse_critique(raw, "Finance")

def marketing_critique(idea: str, proposal: str, fast: bool = False) -> dict:
    prompt = (
        f"You are the CMO reviewing this startup proposal for market traction potential.\n"
        f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
        "Give a 2-3 sentence critique covering positioning and growth channels. "
        "End your response with exactly: [SCORE: X/10] where X is your consensus score (how strong is the market strategy)."
    )
    raw = call_ai(prompt, fast)
    return _parse_critique(raw, "Marketing")

def risk_critique(idea: str, proposal: str, fast: bool = False) -> dict:
    prompt = (
        f"You are the Chief Risk Officer reviewing this startup proposal.\n"
        f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
        "Give a 2-3 sentence critique identifying the top 2 risks and mitigations. "
        "End your response with exactly: [SCORE: X/10] where X is your consensus score (how well does this manage risk)."
    )
    raw = call_ai(prompt, fast)
    return _parse_critique(raw, "Risk")

def _parse_critique(raw: str, agent: str) -> dict:
    """Extract score from critique text."""
    import re
    score = 5  # default
    match = re.search(r'\[SCORE:\s*(\d+(?:\.\d+)?)/10\]', raw, re.IGNORECASE)
    if match:
        score = float(match.group(1))
        raw = raw[:match.start()].strip()
    return {"agent": agent, "content": raw, "score": score}

# ── PHASE 3: CEO Revision ─────────────────────────────────────────────────────

def ceo_revise(idea: str, prev_proposal: str, critiques: list[dict], round_num: int, fast: bool = False) -> str:
    critique_text = "\n".join(
        f"- {c['agent']} (score {c['score']}/10): {c['content']}"
        for c in critiques
    )
    prompt = (
        f"You are the CEO revising your startup proposal (revision round {round_num}).\n"
        f"Startup idea: '{idea}'\n"
        f"Your previous proposal: '{prev_proposal}'\n\n"
        f"Team critique:\n{critique_text}\n\n"
        "Write a revised proposal (3-4 sentences of prose) that directly addresses the team's concerns. "
        "Be specific about how you've improved the financial model, technical approach, or risk strategy."
    )
    return call_ai(prompt, fast)

# ── PHASE 4: Synthesis ────────────────────────────────────────────────────────

def synthesize(idea: str, final_proposal: str, critiques: list[dict], fast: bool = False) -> dict:
    critique_text = "\n".join(
        f"- {c['agent']}: {c['content']}"
        for c in critiques
    )
    prompt = (
        f"You are the Chief Strategy Officer synthesizing a final business plan.\n"
        f"Startup idea: '{idea}'\n"
        f"Final proposal: '{final_proposal}'\n"
        f"Team insights:\n{critique_text}\n\n"
        "Produce a structured business plan with these exact sections separated by '###':\n"
        "### Executive Summary\n"
        "### Technology Stack\n"
        "### Financial Model\n"
        "### Marketing Strategy\n"
        "### Risk Assessment\n\n"
        "Write 2-3 sentences per section. Be concrete and actionable."
    )
    raw = call_ai(prompt, fast)
    return _parse_plan(raw)

def _parse_plan(raw: str) -> dict:
    """Split structured plan into sections."""
    import re
    sections = re.split(r'###\s*', raw)
    plan = {"raw": raw}
    keys = ["Executive Summary", "Technology Stack", "Financial Model", "Marketing Strategy", "Risk Assessment"]
    for section in sections:
        for key in keys:
            if section.strip().startswith(key):
                plan[key] = section[len(key):].strip()
    return plan
