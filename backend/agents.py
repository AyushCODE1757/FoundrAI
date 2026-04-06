# """
# FoundrAI 2.0 — Agent definitions (Tool-Augmented + RAG-Grounded)
# Each agent: 1) fetches live data via @tool  2) CEO/Risk also query ChromaDB RAG  3) LLM synthesizes
# """

# import os
# import re
# from dotenv import load_dotenv
# from huggingface_hub import InferenceClient

# from tools import (
#     search_recent_startups,
#     search_competitors,
#     search_reddit_pain_points,
#     get_google_trends,
#     search_github_repos,
# )
# from rag import query_for_idea, query_for_risks, query_for_pitch

# load_dotenv()

# HF_TOKEN    = os.getenv("HF_TOKEN")
# FAST_MODEL  = "Qwen/Qwen2.5-7B-Instruct"
# NORMAL_MODEL = "Qwen/Qwen2.5-72B-Instruct"


# def get_client():
#     return InferenceClient(api_key=HF_TOKEN)


# def call_ai(prompt: str, fast: bool = False) -> str:
#     if not HF_TOKEN or HF_TOKEN.startswith("your_"):
#         return f"[MOCK] No HF_TOKEN. Prompt preview: {prompt[:60]}..."
#     try:
#         client = get_client()
#         model = FAST_MODEL if fast else NORMAL_MODEL
#         response = client.chat.completions.create(
#             model=model,
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=300,
#             temperature=0.75,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"Error calling AI: {str(e)}"


# def _parse_critique(raw: str, agent: str) -> dict:
#     score = 5.0
#     match = re.search(r'\[SCORE:\s*(\d+(?:\.\d+)?)/10\]', raw, re.IGNORECASE)
#     if match:
#         score = float(match.group(1))
#         raw = raw[:match.start()].strip()
#     return {"agent": agent, "content": raw, "score": score}


# def _parse_plan(raw: str) -> dict:
#     sections = re.split(r'###\s*', raw)
#     plan = {"raw": raw}
#     keys = ["Executive Summary", "Technology Stack", "Financial Model",
#             "Marketing Strategy", "Risk Assessment"]
#     for section in sections:
#         for key in keys:
#             if section.strip().startswith(key):
#                 plan[key] = section[len(key):].strip()
#     return plan


# # ── PHASE 1: CEO Proposal (Grounded by Tavily) ───────────────────────────────

# def ceo_propose(idea: str, fast: bool = False) -> dict:
#     # Step 1: Query ChromaDB knowledge base (YC wisdom + PG essays)
#     rag_context = query_for_idea(idea)

#     # Step 2: Query live web via Tavily
#     query       = f"recent startups {idea} 2024 2025"
#     tool_result = search_recent_startups.invoke(query)
#     snippet     = tool_result[:300]

#     prompt = (
#         f"You are the visionary CEO of a new startup. The idea is: '{idea}'.\n\n"
#         f"[YC & PAUL GRAHAM KNOWLEDGE BASE]\n{rag_context}\n\n"
#         f"[LIVE MARKET DATA from Tavily web search]\n{tool_result}\n\n"
#         "Using BOTH the proven VC wisdom above AND the live market data, draft a concise business proposal "
#         "(3-4 sentences) covering:\n"
#         "1. Core value proposition that differentiates from what already exists\n"
#         "2. Target market (be specific — cite a real segment from the data)\n"
#         "3. Go-to-market strategy grounded in what has worked for similar startups\n"
#         "Reference specific competitors, PG insights, or YC patterns. Write in prose, no bullet points."
#     )
#     content = call_ai(prompt, fast)
#     return {
#         "agent": "CEO",
#         "tool_name": "Tavily Web Search",
#         "tool_query": query,
#         "tool_result_snippet": snippet,
#         "rag_used": True,
#         "content": content,
#     }


# # ── PHASE 2: Developer Critique (Grounded by GitHub) ─────────────────────────

# def dev_critique(idea: str, proposal: str, fast: bool = False) -> dict:
#     query       = f"{idea} open source"
#     tool_result = search_github_repos.invoke(query)
#     snippet     = tool_result[:300]

#     prompt = (
#         f"You are the Lead Developer reviewing this startup proposal for technical feasibility.\n"
#         f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
#         f"[LIVE GITHUB DATA — similar repos already in this space]\n{tool_result}\n\n"
#         "Using the GitHub data above, give a 2-3 sentence critique covering:\n"
#         "- Whether the tech stack has community support (cite actual repos/languages found)\n"
#         "- Key technical risks or build-vs-buy decisions\n"
#         "End with exactly: [SCORE: X/10]"
#     )
#     raw = call_ai(prompt, fast)
#     result = _parse_critique(raw, "Developer")
#     result.update({"tool_name": "GitHub Search API", "tool_query": query,
#                    "tool_result_snippet": snippet})
#     return result


# # ── PHASE 2: Finance Critique (Grounded by PyTrends) ─────────────────────────

# def finance_critique(idea: str, proposal: str, fast: bool = False) -> dict:
#     query       = " ".join(idea.split()[:3])
#     tool_result = get_google_trends.invoke(query)
#     snippet     = tool_result[:300]

#     prompt = (
#         f"You are the CFO reviewing this startup proposal for financial viability.\n"
#         f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
#         f"[LIVE GOOGLE TRENDS DATA]\n{tool_result}\n\n"
#         "Using the trend data above, give a 2-3 sentence critique covering:\n"
#         "- Whether market demand is growing or shrinking (cite the trend numbers)\n"
#         "- Estimated costs and a realistic revenue model\n"
#         "End with exactly: [SCORE: X/10]"
#     )
#     raw = call_ai(prompt, fast)
#     result = _parse_critique(raw, "Finance")
#     result.update({"tool_name": "Google Trends (PyTrends)", "tool_query": query,
#                    "tool_result_snippet": snippet})
#     return result


# # ── PHASE 2: Marketing Critique (Grounded by Tavily Competitors) ─────────────

# def marketing_critique(idea: str, proposal: str, fast: bool = False) -> dict:
#     query       = f"{idea} competitor pricing"
#     tool_result = search_competitors.invoke(query)
#     snippet     = tool_result[:300]

#     prompt = (
#         f"You are the CMO reviewing this startup proposal for market traction potential.\n"
#         f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
#         f"[LIVE COMPETITOR INTELLIGENCE from Tavily]\n{tool_result}\n\n"
#         "Using the real competitor data above, give a 2-3 sentence critique covering:\n"
#         "- Name specific competitors and their pricing or weaknesses (use the data!)\n"
#         "- Best growth channel and our differentiation strategy\n"
#         "End with exactly: [SCORE: X/10]"
#     )
#     raw = call_ai(prompt, fast)
#     result = _parse_critique(raw, "Marketing")
#     result.update({"tool_name": "Tavily Competitor Intel", "tool_query": query,
#                    "tool_result_snippet": snippet})
#     return result


# # ── PHASE 2: Risk Critique (Grounded by Reddit/PRAW) ─────────────────────────

# def risk_critique(idea: str, proposal: str, fast: bool = False) -> dict:
#     # Step 1: Query ChromaDB for failure post-mortems
#     rag_failures = query_for_risks(idea)

#     # Step 2: Live Reddit data
#     query       = " ".join(idea.split()[:4])
#     tool_result = search_reddit_pain_points.invoke(query)
#     snippet     = tool_result[:300]

#     prompt = (
#         f"You are the Chief Risk Officer reviewing this startup proposal.\n"
#         f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
#         f"[STARTUP FAILURE POST-MORTEMS from knowledge base]\n{rag_failures}\n\n"
#         f"[LIVE REDDIT COMMUNITY DATA — real user pain points]\n{tool_result}\n\n"
#         "Using BOTH the failure patterns above AND the Reddit data, give a 2-3 sentence critique covering:\n"
#         "- Which known startup failure pattern (from the knowledge base) does this idea risk repeating?\n"
#         "- How validated is this problem from Reddit data? (cite actual posts if found)\n"
#         "- Top 2 risks with specific mitigation strategies\n"
#         "End with exactly: [SCORE: X/10]"
#     )
#     raw = call_ai(prompt, fast)
#     result = _parse_critique(raw, "Risk")
#     result.update({"tool_name": "Reddit API (PRAW)", "tool_query": query,
#                    "tool_result_snippet": snippet, "rag_used": True})
#     return result


# # ── PHASE 3: CEO Revision ─────────────────────────────────────────────────────

# def ceo_revise(idea: str, prev_proposal: str, critiques: list, round_num: int,
#                fast: bool = False) -> dict:
#     critique_text = "\n".join(
#         f"- {c['agent']} (score {c['score']}/10): {c['content']}"
#         for c in critiques
#     )
#     prompt = (
#         f"You are the CEO revising your startup proposal (round {round_num}).\n"
#         f"Idea: '{idea}'\nPrevious proposal: '{prev_proposal}'\n\n"
#         f"Team critique (grounded in real data):\n{critique_text}\n\n"
#         "Write a revised proposal (3-4 sentences of prose) that directly addresses each concern. "
#         "Reference specific improvements to the financial model, tech approach, or risk strategy."
#     )
#     content = call_ai(prompt, fast)
#     return {
#         "agent": "CEO",
#         "tool_name": None,
#         "tool_query": None,
#         "tool_result_snippet": None,
#         "content": content,
#     }


# # ── PHASE 4: Synthesis ────────────────────────────────────────────────────────

# def synthesize(idea: str, final_proposal: str, critiques: list,
#                fast: bool = False) -> dict:
#     critique_text = "\n".join(
#         f"- {c['agent']} (grounded in {c.get('tool_name','LLM')}): {c['content']}"
#         for c in critiques
#     )
#     prompt = (
#         f"You are the Chief Strategy Officer synthesizing a final business plan.\n"
#         f"Idea: '{idea}'\nFinal proposal: '{final_proposal}'\n"
#         f"Agent insights (from real-world data):\n{critique_text}\n\n"
#         "Produce a structured business plan with these exact sections separated by '###':\n"
#         "### Executive Summary\n### Technology Stack\n### Financial Model\n"
#         "### Marketing Strategy\n### Risk Assessment\n\n"
#         "Write 2-3 concrete, actionable sentences per section. Cite real data from agent critiques."
#     )
#     raw = call_ai(prompt, fast)
#     return _parse_plan(raw)


# # ── DEPLOY: Generate Boilerplate Codebase ────────────────────────────────────

# def generate_boilerplate(idea: str, plan: dict) -> dict:
#     """
#     LLM generates a starter codebase based on the validated business plan.
#     Returns a dict of {filename: content} ready to push to GitHub.
#     """
#     tech_stack = plan.get("Technology Stack", "FastAPI backend, React frontend")

#     prompt = (
#         f"You are a senior developer generating starter boilerplate for a new startup.\n"
#         f"Startup idea: '{idea}'\n"
#         f"Tech stack from business plan: {tech_stack}\n\n"
#         "Generate EXACTLY these 4 files. Use '=== FILENAME ===' as a separator.\n\n"
#         "=== README.md ===\n"
#         "(A compelling README with: project name, one-line description, setup instructions, "
#         "tech stack, and how to run locally. Use markdown.)\n\n"
#         "=== docker-compose.yml ===\n"
#         "(A working docker-compose.yml appropriate for the tech stack. Use realistic service names.)\n\n"
#         "=== .env.example ===\n"
#         "(All environment variables the app would need, with placeholder values and comments.)\n\n"
#         "=== app/main.py ===\n"
#         "(A real, runnable Python entrypoint — FastAPI or equivalent — with 2-3 working API routes "
#         "relevant to the startup idea. Include docstrings.)\n\n"
#         "Generate all 4 files now. Be concrete and specific to this startup, not generic boilerplate."
#     )

#     raw = call_ai(prompt, fast=False)

#     # Parse sections
#     files = {}
#     file_names = ["README.md", "docker-compose.yml", ".env.example", "app/main.py"]
#     for fname in file_names:
#         marker = f"=== {fname} ==="
#         if marker in raw:
#             start = raw.index(marker) + len(marker)
#             # Find the next marker or end
#             next_markers = [raw.index(f"=== {n} ===") for n in file_names
#                             if f"=== {n} ===" in raw and raw.index(f"=== {n} ===") > start]
#             end = min(next_markers) if next_markers else len(raw)
#             files[fname] = raw[start:end].strip()

#     # Always include a foundrai.json manifest
#     import json as _json
#     files["foundrai.json"] = _json.dumps({
#         "generated_by": "FoundrAI 2.0",
#         "idea": idea,
#         "tech_stack": tech_stack,
#         "validated": True,
#     }, indent=2)

#     return files


# # ── MONITOR: Auto-Strategy Update (Fast-Forward Simulator) ───────────────────

# def generate_monitor_update(idea: str, new_market_data: str) -> str:
#     """
#     Given new market signals, generate a revised Marketing Strategy section.
#     Used by the Auto-Monitor daemon (and the Fast-Forward demo button).
#     """
#     prompt = (
#         f"You are a startup strategist responding to NEW market intelligence.\n"
#         f"Startup idea: '{idea}'\n\n"
#         f"[NEW MARKET SIGNALS DETECTED]\n{new_market_data}\n\n"
#         "Based on these new signals, write a revised Marketing Strategy (2-3 sentences) that:\n"
#         "- Directly responds to the new competitor or trend detected\n"
#         "- Adjusts the growth channel or positioning accordingly\n"
#         "- Is concrete and actionable\n"
#         "Start your response with '⚡ UPDATED:'"
#     )
#     return call_ai(prompt, fast=True)


# """
# FoundrAI 2.0 — Agent definitions (Tool-Augmented + RAG-Grounded)
# Each agent: 1) fetches live data via @tool  2) CEO/Risk also query ChromaDB RAG  3) LLM synthesizes
# """

# import os
# import re
# import json as _json
# from dotenv import load_dotenv
# from huggingface_hub import InferenceClient

# from tools import (
#     search_recent_startups,
#     search_competitors,
#     search_reddit_pain_points,
#     get_google_trends,
#     search_github_repos,
# )
# from rag import query_for_idea, query_for_risks, query_for_pitch

# load_dotenv()

# HF_TOKEN     = os.getenv("HF_TOKEN")
# FAST_MODEL   = "Qwen/Qwen2.5-7B-Instruct"
# NORMAL_MODEL = "Qwen/Qwen2.5-72B-Instruct"


# def get_client():
#     return InferenceClient(api_key=HF_TOKEN)


# def call_ai(prompt: str, fast: bool = False) -> str:
#     if not HF_TOKEN or HF_TOKEN.startswith("your_"):
#         return f"[MOCK] No HF_TOKEN. Prompt preview: {prompt[:60]}..."
#     try:
#         client = get_client()
#         model  = FAST_MODEL if fast else NORMAL_MODEL
#         response = client.chat.completions.create(
#             model=model,
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=300,
#             temperature=0.75,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"Error calling AI: {str(e)}"


# def _parse_critique(raw: str, agent: str) -> dict:
#     score = 5.0
#     match = re.search(r'\[SCORE:\s*(\d+(?:\.\d+)?)/10\]', raw, re.IGNORECASE)
#     if match:
#         score = float(match.group(1))
#         raw   = raw[:match.start()].strip()
#     return {"agent": agent, "content": raw, "score": score}


# def _parse_plan(raw: str) -> dict:
#     sections = re.split(r'###\s*', raw)
#     plan     = {"raw": raw}
#     keys     = ["Executive Summary", "Technology Stack", "Financial Model",
#                 "Marketing Strategy", "Risk Assessment"]
#     for section in sections:
#         for key in keys:
#             if section.strip().startswith(key):
#                 plan[key] = section[len(key):].strip()
#     return plan


# # ── PHASE 1: CEO Proposal ─────────────────────────────────────────────────────

# def ceo_propose(idea: str, fast: bool = False) -> dict:
#     rag_context = query_for_idea(idea)
#     query       = f"recent startups {idea} 2024 2025"
#     tool_result = search_recent_startups.invoke(query)
#     snippet     = tool_result[:300]

#     prompt = (
#         f"You are the visionary CEO of a new startup. The idea is: '{idea}'.\n\n"
#         f"[YC & PAUL GRAHAM KNOWLEDGE BASE]\n{rag_context}\n\n"
#         f"[LIVE MARKET DATA from Tavily web search]\n{tool_result}\n\n"
#         "Using BOTH the proven VC wisdom above AND the live market data, draft a concise business proposal "
#         "(3-4 sentences) covering:\n"
#         "1. Core value proposition that differentiates from what already exists\n"
#         "2. Target market (be specific — cite a real segment from the data)\n"
#         "3. Go-to-market strategy grounded in what has worked for similar startups\n"
#         "Reference specific competitors, PG insights, or YC patterns. Write in prose, no bullet points."
#     )
#     content = call_ai(prompt, fast)
#     return {
#         "agent": "CEO",
#         "tool_name": "Tavily Web Search",
#         "tool_query": query,
#         "tool_result_snippet": snippet,
#         "rag_used": True,
#         "content": content,
#     }


# # ── PHASE 2: Developer Critique ───────────────────────────────────────────────

# def dev_critique(idea: str, proposal: str, fast: bool = False) -> dict:
#     query       = f"{idea} open source"
#     tool_result = search_github_repos.invoke(query)
#     snippet     = tool_result[:300]

#     prompt = (
#         f"You are the Lead Developer reviewing this startup proposal for technical feasibility.\n"
#         f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
#         f"[LIVE GITHUB DATA — similar repos already in this space]\n{tool_result}\n\n"
#         "Using the GitHub data above, give a 2-3 sentence critique covering:\n"
#         "- Whether the tech stack has community support (cite actual repos/languages found)\n"
#         "- Key technical risks or build-vs-buy decisions\n"
#         "End with exactly: [SCORE: X/10]"
#     )
#     raw    = call_ai(prompt, fast)
#     result = _parse_critique(raw, "Developer")
#     result.update({"tool_name": "GitHub Search API", "tool_query": query,
#                    "tool_result_snippet": snippet})
#     return result


# # ── PHASE 2: Finance Critique ─────────────────────────────────────────────────

# def finance_critique(idea: str, proposal: str, fast: bool = False) -> dict:
#     query       = " ".join(idea.split()[:3])
#     tool_result = get_google_trends.invoke(query)
#     snippet     = tool_result[:300]

#     prompt = (
#         f"You are the CFO reviewing this startup proposal for financial viability.\n"
#         f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
#         f"[LIVE GOOGLE TRENDS DATA]\n{tool_result}\n\n"
#         "Using the trend data above, give a 2-3 sentence critique covering:\n"
#         "- Whether market demand is growing or shrinking (cite the trend numbers)\n"
#         "- Estimated costs and a realistic revenue model\n"
#         "End with exactly: [SCORE: X/10]"
#     )
#     raw    = call_ai(prompt, fast)
#     result = _parse_critique(raw, "Finance")
#     result.update({"tool_name": "Google Trends (PyTrends)", "tool_query": query,
#                    "tool_result_snippet": snippet})
#     return result


# # ── PHASE 2: Marketing Critique ───────────────────────────────────────────────

# def marketing_critique(idea: str, proposal: str, fast: bool = False) -> dict:
#     query       = f"{idea} competitor pricing"
#     tool_result = search_competitors.invoke(query)
#     snippet     = tool_result[:300]

#     prompt = (
#         f"You are the CMO reviewing this startup proposal for market traction potential.\n"
#         f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
#         f"[LIVE COMPETITOR INTELLIGENCE from Tavily]\n{tool_result}\n\n"
#         "Using the real competitor data above, give a 2-3 sentence critique covering:\n"
#         "- Name specific competitors and their pricing or weaknesses (use the data!)\n"
#         "- Best growth channel and our differentiation strategy\n"
#         "End with exactly: [SCORE: X/10]"
#     )
#     raw    = call_ai(prompt, fast)
#     result = _parse_critique(raw, "Marketing")
#     result.update({"tool_name": "Tavily Competitor Intel", "tool_query": query,
#                    "tool_result_snippet": snippet})
#     return result


# # ── PHASE 2: Risk Critique ────────────────────────────────────────────────────

# def risk_critique(idea: str, proposal: str, fast: bool = False) -> dict:
#     rag_failures = query_for_risks(idea)
#     query        = " ".join(idea.split()[:4])
#     tool_result  = search_reddit_pain_points.invoke(query)
#     snippet      = tool_result[:300]

#     prompt = (
#         f"You are the Chief Risk Officer reviewing this startup proposal.\n"
#         f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
#         f"[STARTUP FAILURE POST-MORTEMS from knowledge base]\n{rag_failures}\n\n"
#         f"[LIVE REDDIT COMMUNITY DATA — real user pain points]\n{tool_result}\n\n"
#         "Using BOTH the failure patterns above AND the Reddit data, give a 2-3 sentence critique covering:\n"
#         "- Which known startup failure pattern (from the knowledge base) does this idea risk repeating?\n"
#         "- How validated is this problem from Reddit data? (cite actual posts if found)\n"
#         "- Top 2 risks with specific mitigation strategies\n"
#         "End with exactly: [SCORE: X/10]"
#     )
#     raw    = call_ai(prompt, fast)
#     result = _parse_critique(raw, "Risk")
#     result.update({"tool_name": "Reddit API (PRAW)", "tool_query": query,
#                    "tool_result_snippet": snippet, "rag_used": True})
#     return result


# # ── PHASE 3: CEO Revision ─────────────────────────────────────────────────────

# def ceo_revise(idea: str, prev_proposal: str, critiques: list,
#                round_num: int, fast: bool = False) -> dict:
#     critique_text = "\n".join(
#         f"- {c['agent']} (score {c['score']}/10): {c['content']}"
#         for c in critiques
#     )
#     prompt = (
#         f"You are the CEO revising your startup proposal (round {round_num}).\n"
#         f"Idea: '{idea}'\nPrevious proposal: '{prev_proposal}'\n\n"
#         f"Team critique (grounded in real data):\n{critique_text}\n\n"
#         "Write a revised proposal (3-4 sentences of prose) that directly addresses each concern. "
#         "Reference specific improvements to the financial model, tech approach, or risk strategy."
#     )
#     content = call_ai(prompt, fast)
#     return {
#         "agent": "CEO",
#         "tool_name": None,
#         "tool_query": None,
#         "tool_result_snippet": None,
#         "content": content,
#     }


# # ── PHASE 4: Synthesis ────────────────────────────────────────────────────────

# def synthesize(idea: str, final_proposal: str, critiques: list,
#                fast: bool = False) -> dict:
#     critique_text = "\n".join(
#         f"- {c['agent']} (grounded in {c.get('tool_name','LLM')}): {c['content']}"
#         for c in critiques
#     )
#     prompt = (
#         f"You are the Chief Strategy Officer synthesizing a final business plan.\n"
#         f"Idea: '{idea}'\nFinal proposal: '{final_proposal}'\n"
#         f"Agent insights (from real-world data):\n{critique_text}\n\n"
#         "Produce a structured business plan with these exact sections separated by '###':\n"
#         "### Executive Summary\n### Technology Stack\n### Financial Model\n"
#         "### Marketing Strategy\n### Risk Assessment\n\n"
#         "Write 2-3 concrete, actionable sentences per section. Cite real data from agent critiques."
#     )
#     raw = call_ai(prompt, fast)
#     return _parse_plan(raw)


# # ── DEPLOY: Generate Boilerplate Codebase ────────────────────────────────────

# def generate_boilerplate(idea: str, plan: dict) -> dict:
#     """
#     Generates a rich, startup-specific codebase based on the validated plan.
#     Returns {filename: content} ready to push to GitHub.

#     FIXED: Uses structured data from all plan sections to build a detailed README
#     and real files — no longer generic boilerplate.
#     """
#     tech_stack      = plan.get("Technology Stack", "FastAPI backend, React frontend, PostgreSQL")
#     exec_summary    = plan.get("Executive Summary", "")
#     financial_model = plan.get("Financial Model", "")
#     marketing       = plan.get("Marketing Strategy", "")
#     risk            = plan.get("Risk Assessment", "")

#     # ── Derive a clean project name from the idea ──────────────────────────
#     project_name = "-".join(idea.lower().split()[:4])
#     project_name = re.sub(r"[^a-z0-9\-]", "", project_name).strip("-")
#     class_name   = "".join(w.capitalize() for w in idea.split()[:3])

#     # ── 1. README.md — rich and detailed ──────────────────────────────────
#     readme = f"""# {idea}

# > {exec_summary[:200] if exec_summary else 'An AI-validated startup built with FoundrAI 2.0.'}

# [![FoundrAI](https://img.shields.io/badge/Generated%20by-FoundrAI%202.0-6366f1?style=flat-square)](https://github.com/foundr-ai)
# [![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

# ---

# ## 📋 Executive Summary

# {exec_summary if exec_summary else '_See business plan PDF for full summary._'}

# ---

# ## 🏗️ Tech Stack

# {tech_stack if tech_stack else '_See Technology Stack section of business plan._'}

# | Layer | Technology | Purpose | Cost |
# |---|---|---|---|
# | Agent Orchestration | CrewAI | Agent roles and task routing | Free |
# | Tool Framework | LangChain | @tool wrappers for all APIs | Free |
# | LLM | Qwen2.5-72B / Claude | Reasoning & generation | Free/API |
# | Web Search | Tavily API | Live market research | Free tier |
# | Social Validation | Reddit (PRAW) | Community pain point scan | Free |
# | Market Trends | PyTrends | Google Trends validation | Free |
# | Vector Memory | ChromaDB | RAG knowledge base | Free, local |
# | Code Deployment | GitHub API (PyGithub) | Autonomous repo creation | Free |
# | PDF Export | ReportLab | Business plan PDF | Free |
# | Backend | FastAPI + Uvicorn | API and SSE streaming | Free |
# | Frontend | React + Next.js | UI with live agent cards | Free |
# | Containerization | Docker + Docker Compose | Production deployment | Free |

# ---

# ## 💰 Financial Model

# {financial_model if financial_model else '_See Financial Model section of business plan._'}

# ---

# ## 📣 Marketing Strategy

# {marketing if marketing else '_See Marketing Strategy section of business plan._'}

# ---

# ## ⚠️ Risk Assessment

# {risk if risk else '_See Risk Assessment section of business plan._'}

# ---

# ## 🚀 Quick Start

# ### Prerequisites
# - Docker & Docker Compose
# - Python 3.11+
# - Node.js 18+

# ### 1. Clone and configure
# ```bash
# git clone https://github.com/your-org/{project_name}
# cd {project_name}
# cp .env.example .env
# # Edit .env with your API keys
# ```

# ### 2. Run with Docker
# ```bash
# docker compose up --build
# ```

# ### 3. Run locally
# ```bash
# # Backend
# pip install -r requirements.txt
# uvicorn app.main:app --reload --port 8000

# # Frontend (separate terminal)
# cd frontend
# npm install && npm run dev
# ```

# ### 4. Access
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Frontend: http://localhost:3000

# ---

# ## 📁 Project Structure

# ```
# {project_name}/
# ├── app/
# │   └── main.py          # FastAPI entry point
# ├── frontend/            # Next.js frontend
# ├── docker-compose.yml   # Container orchestration
# ├── requirements.txt     # Python dependencies
# ├── .env.example         # Environment variable template
# └── README.md
# ```

# ---

# ## 🤖 Generated by FoundrAI 2.0

# This project was validated by a multi-agent AI consensus system:
# - **CEO Agent** researched live market data via Tavily
# - **Dev Agent** validated tech stack via GitHub API
# - **Finance Agent** confirmed demand via Google Trends
# - **Marketing Agent** analysed competitors via Tavily
# - **Risk Agent** scanned community pain points via Reddit

# Consensus score achieved before generation.

# ---

# *Built with [FoundrAI 2.0](https://github.com/foundr-ai) — Autonomous Business Validation Engine*
# """

#     # ── 2. docker-compose.yml — based on tech stack ────────────────────────
#     docker_compose = f"""version: '3.9'

# services:
#   api:
#     build:
#       context: .
#       dockerfile: Dockerfile
#     container_name: {project_name}_api
#     ports:
#       - "8000:8000"
#     environment:
#       - DATABASE_URL=${{DATABASE_URL}}
#       - SECRET_KEY=${{SECRET_KEY}}
#       - ENVIRONMENT=production
#     env_file:
#       - .env
#     depends_on:
#       - db
#     restart: unless-stopped
#     volumes:
#       - ./app:/app/app

#   db:
#     image: postgres:15-alpine
#     container_name: {project_name}_db
#     ports:
#       - "5432:5432"
#     environment:
#       POSTGRES_DB: {project_name.replace('-','_')}
#       POSTGRES_USER: ${{POSTGRES_USER:-appuser}}
#       POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD}}
#     volumes:
#       - postgres_data:/var/lib/postgresql/data
#     restart: unless-stopped
#     healthcheck:
#       test: ["CMD-SHELL", "pg_isready -U ${{POSTGRES_USER:-appuser}}"]
#       interval: 10s
#       timeout: 5s
#       retries: 5

#   frontend:
#     build:
#       context: ./frontend
#       dockerfile: Dockerfile
#     container_name: {project_name}_frontend
#     ports:
#       - "3000:3000"
#     environment:
#       - NEXT_PUBLIC_API_URL=http://api:8000
#     depends_on:
#       - api
#     restart: unless-stopped

# volumes:
#   postgres_data:
# """

#     # ── 3. .env.example ────────────────────────────────────────────────────
#     env_example = f"""# {idea} — Environment Variables
# # Copy this file to .env and fill in your values

# # ── Database ──────────────────────────────────────────────────────────────
# DATABASE_URL=postgresql://appuser:yourpassword@db:5432/{project_name.replace('-','_')}
# POSTGRES_USER=appuser
# POSTGRES_PASSWORD=change_me_in_production

# # ── App Security ──────────────────────────────────────────────────────────
# SECRET_KEY=your-256-bit-secret-key-here
# ENVIRONMENT=development                # development | production

# # ── External APIs ─────────────────────────────────────────────────────────
# # Tavily — live web search (get key at tavily.com)
# TAVILY_API_KEY=tvly-your-key-here

# # HuggingFace — LLM inference
# HF_TOKEN=hf_your_token_here

# # GitHub — autonomous deployment
# GITHUB_TOKEN=ghp_your_token_here
# GITHUB_ORG=                           # leave blank to use personal account

# # OpenAI (optional fallback LLM)
# OPENAI_API_KEY=sk-your-key-here

# # ── Frontend ──────────────────────────────────────────────────────────────
# NEXT_PUBLIC_API_URL=http://localhost:8000
# """

#     # ── 4. app/main.py — real working FastAPI with idea-specific routes ────
#     main_py = f"""\"\"\"
# {idea} — FastAPI Backend
# Generated by FoundrAI 2.0

# Tech Stack: {tech_stack[:120] if tech_stack else 'FastAPI, PostgreSQL'}
# \"\"\"

# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Optional
# import os

# app = FastAPI(
#     title="{idea}",
#     description="{exec_summary[:150] if exec_summary else 'AI-validated startup API'}",
#     version="0.1.0",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # ── Models ────────────────────────────────────────────────────────────────────

# class UserCreate(BaseModel):
#     email: str
#     name: str
#     password: str


# class UserResponse(BaseModel):
#     id: int
#     email: str
#     name: str


# class ItemCreate(BaseModel):
#     title: str
#     description: Optional[str] = None


# # ── Routes ────────────────────────────────────────────────────────────────────

# @app.get("/")
# async def root():
#     \"\"\"Health check and project info.\"\"\"
#     return {{
#         "project": "{idea}",
#         "version": "0.1.0",
#         "status": "running",
#         "generated_by": "FoundrAI 2.0",
#     }}


# @app.get("/health")
# async def health():
#     \"\"\"Kubernetes/Docker health probe endpoint.\"\"\"
#     return {{"status": "ok"}}


# @app.post("/users", response_model=dict, status_code=201)
# async def create_user(user: UserCreate):
#     \"\"\"
#     Register a new user.
#     TODO: connect to PostgreSQL via SQLAlchemy or asyncpg.
#     \"\"\"
#     # Replace with real DB call
#     return {{
#         "id": 1,
#         "email": user.email,
#         "name": user.name,
#         "message": "User created successfully",
#     }}


# @app.get("/users/{{user_id}}")
# async def get_user(user_id: int):
#     \"\"\"Fetch a user by ID.\"\"\"
#     # Replace with real DB call
#     if user_id != 1:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {{"id": user_id, "email": "demo@example.com", "name": "Demo User"}}


# @app.post("/items", status_code=201)
# async def create_item(item: ItemCreate):
#     \"\"\"
#     Core business entity endpoint — customise to match your domain.
#     e.g. for a food app this becomes POST /meals, for SaaS POST /projects
#     \"\"\"
#     return {{
#         "id": 1,
#         "title": item.title,
#         "description": item.description,
#         "status": "created",
#     }}


# @app.get("/items")
# async def list_items(skip: int = 0, limit: int = 20):
#     \"\"\"List all items with pagination.\"\"\"
#     return {{
#         "items": [],
#         "total": 0,
#         "skip": skip,
#         "limit": limit,
#     }}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# """

#     # ── 5. requirements.txt ────────────────────────────────────────────────
#     requirements = """fastapi>=0.110.0
# uvicorn[standard]>=0.29.0
# pydantic>=2.0.0
# python-dotenv>=1.0.0
# sqlalchemy>=2.0.0
# asyncpg>=0.29.0
# alembic>=1.13.0
# httpx>=0.27.0
# python-jose[cryptography]>=3.3.0
# passlib[bcrypt]>=1.7.4
# python-multipart>=0.0.9
# """

#     # ── 6. foundrai.json manifest ──────────────────────────────────────────
#     manifest = _json.dumps({
#         "generated_by": "FoundrAI 2.0",
#         "idea": idea,
#         "tech_stack": tech_stack,
#         "consensus_validated": True,
#         "plan_sections": list(plan.keys()),
#     }, indent=2)

#     return {
#         "README.md":           readme,
#         "docker-compose.yml":  docker_compose,
#         ".env.example":        env_example,
#         "app/main.py":         main_py,
#         "requirements.txt":    requirements,
#         "foundrai.json":       manifest,
#     }


# # ── MONITOR: Auto-Strategy Update ────────────────────────────────────────────

# def generate_monitor_update(idea: str, new_market_data: str) -> str:
#     """
#     Given new market signals, generate a revised Marketing Strategy section.
#     Used by the Auto-Monitor daemon (and the Fast-Forward demo button).
#     """
#     prompt = (
#         f"You are a startup strategist responding to NEW market intelligence.\n"
#         f"Startup idea: '{idea}'\n\n"
#         f"[NEW MARKET SIGNALS DETECTED]\n{new_market_data}\n\n"
#         "Based on these new signals, write a revised Marketing Strategy (2-3 sentences) that:\n"
#         "- Directly responds to the new competitor or trend detected\n"
#         "- Adjusts the growth channel or positioning accordingly\n"
#         "- Is concrete and actionable\n"
#         "Start your response with '⚡ UPDATED:'"
#     )
#     return call_ai(prompt, fast=True)


"""
FoundrAI 2.0 — Agent definitions (Tool-Augmented + RAG-Grounded)
Each agent: 1) fetches live data via @tool  2) CEO/Risk also query ChromaDB RAG  3) LLM synthesizes
"""

import os
import re
import json as _json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from tools import (
    search_recent_startups,
    search_competitors,
    search_reddit_pain_points,
    get_google_trends,
    search_github_repos,
)
from rag import query_for_idea, query_for_risks, query_for_pitch

load_dotenv()

HF_TOKEN     = os.getenv("HF_TOKEN")
FAST_MODEL   = "Qwen/Qwen2.5-7B-Instruct"
NORMAL_MODEL = "Qwen/Qwen2.5-72B-Instruct"


def get_client():
    return InferenceClient(api_key=HF_TOKEN)


def call_ai(prompt: str, fast: bool = False) -> str:
    if not HF_TOKEN or HF_TOKEN.startswith("your_"):
        return f"[MOCK] No HF_TOKEN. Prompt preview: {prompt[:60]}..."
    try:
        client   = get_client()
        model    = FAST_MODEL if fast else NORMAL_MODEL
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,   # increased from 300 to allow detailed synthesis
            temperature=0.75,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling AI: {str(e)}"


def _parse_critique(raw: str, agent: str) -> dict:
    score = 5.0
    match = re.search(r'\[SCORE:\s*(\d+(?:\.\d+)?)/10\]', raw, re.IGNORECASE)
    if match:
        score = float(match.group(1))
        raw   = raw[:match.start()].strip()
    return {"agent": agent, "content": raw, "score": score}


def _parse_plan(raw: str) -> dict:
    """
    Parse LLM output into plan sections.
    Handles both '### Section Name' and '## Section Name' delimiters.
    """
    plan = {"raw": raw}
    keys = [
        "Executive Summary",
        "Technology Stack",
        "Financial Model",
        "Marketing Strategy",
        "Risk Assessment",
    ]
    # Try splitting on ### first, then ##
    sections = re.split(r'#{2,3}\s*', raw)
    for section in sections:
        section = section.strip()
        for key in keys:
            if section.startswith(key):
                content = section[len(key):].strip()
                # Strip leading colon or newline
                content = content.lstrip(": \n")
                if content:
                    plan[key] = content
    return plan


# ── PHASE 1: CEO Proposal ─────────────────────────────────────────────────────

def ceo_propose(idea: str, fast: bool = False) -> dict:
    rag_context = query_for_idea(idea)
    query       = f"recent startups {idea} 2024 2025"
    tool_result = search_recent_startups.invoke(query)
    snippet     = tool_result[:300]

    prompt = (
        f"You are the visionary CEO of a new startup. The idea is: '{idea}'.\n\n"
        f"[YC & PAUL GRAHAM KNOWLEDGE BASE]\n{rag_context}\n\n"
        f"[LIVE MARKET DATA from Tavily web search]\n{tool_result}\n\n"
        "Using BOTH the proven VC wisdom above AND the live market data, draft a concise business proposal "
        "(3-4 sentences) covering:\n"
        "1. Core value proposition that differentiates from what already exists\n"
        "2. Target market (be specific — cite a real segment from the data)\n"
        "3. Go-to-market strategy grounded in what has worked for similar startups\n"
        "Reference specific competitors, PG insights, or YC patterns. Write in prose, no bullet points."
    )
    content = call_ai(prompt, fast)
    return {
        "agent": "CEO",
        "tool_name": "Tavily Web Search",
        "tool_query": query,
        "tool_result_snippet": snippet,
        "rag_used": True,
        "content": content,
    }


# ── PHASE 2: Developer Critique ───────────────────────────────────────────────

def dev_critique(idea: str, proposal: str, fast: bool = False) -> dict:
    query       = f"{idea} open source"
    tool_result = search_github_repos.invoke(query)
    snippet     = tool_result[:300]

    prompt = (
        f"You are the Lead Developer reviewing this startup proposal for technical feasibility.\n"
        f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
        f"[LIVE GITHUB DATA — similar repos already in this space]\n{tool_result}\n\n"
        "Using the GitHub data above, give a 2-3 sentence critique covering:\n"
        "- Whether the tech stack has community support (cite actual repos/languages found)\n"
        "- Key technical risks or build-vs-buy decisions\n"
        "End with exactly: [SCORE: X/10]"
    )
    raw    = call_ai(prompt, fast)
    result = _parse_critique(raw, "Developer")
    result.update({
        "tool_name": "GitHub Search API",
        "tool_query": query,
        "tool_result_snippet": snippet,
    })
    return result


# ── PHASE 2: Finance Critique ─────────────────────────────────────────────────

def finance_critique(idea: str, proposal: str, fast: bool = False) -> dict:
    query       = " ".join(idea.split()[:3])
    tool_result = get_google_trends.invoke(query)
    snippet     = tool_result[:300]

    prompt = (
        f"You are the CFO reviewing this startup proposal for financial viability.\n"
        f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
        f"[LIVE GOOGLE TRENDS DATA]\n{tool_result}\n\n"
        "Using the trend data above, give a 2-3 sentence critique covering:\n"
        "- Whether market demand is growing or shrinking (cite the trend numbers)\n"
        "- Estimated costs and a realistic revenue model\n"
        "End with exactly: [SCORE: X/10]"
    )
    raw    = call_ai(prompt, fast)
    result = _parse_critique(raw, "Finance")
    result.update({
        "tool_name": "Google Trends (PyTrends)",
        "tool_query": query,
        "tool_result_snippet": snippet,
    })
    return result


# ── PHASE 2: Marketing Critique ───────────────────────────────────────────────

def marketing_critique(idea: str, proposal: str, fast: bool = False) -> dict:
    query       = f"{idea} competitor pricing"
    tool_result = search_competitors.invoke(query)
    snippet     = tool_result[:300]

    prompt = (
        f"You are the CMO reviewing this startup proposal for market traction potential.\n"
        f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
        f"[LIVE COMPETITOR INTELLIGENCE from Tavily]\n{tool_result}\n\n"
        "Using the real competitor data above, give a 2-3 sentence critique covering:\n"
        "- Name specific competitors and their pricing or weaknesses (use the data!)\n"
        "- Best growth channel and our differentiation strategy\n"
        "End with exactly: [SCORE: X/10]"
    )
    raw    = call_ai(prompt, fast)
    result = _parse_critique(raw, "Marketing")
    result.update({
        "tool_name": "Tavily Competitor Intel",
        "tool_query": query,
        "tool_result_snippet": snippet,
    })
    return result


# ── PHASE 2: Risk Critique ────────────────────────────────────────────────────

def risk_critique(idea: str, proposal: str, fast: bool = False) -> dict:
    rag_failures = query_for_risks(idea)
    query        = " ".join(idea.split()[:4])
    tool_result  = search_reddit_pain_points.invoke(query)
    snippet      = tool_result[:300]

    prompt = (
        f"You are the Chief Risk Officer reviewing this startup proposal.\n"
        f"Startup idea: '{idea}'\nProposal: '{proposal}'\n\n"
        f"[STARTUP FAILURE POST-MORTEMS from knowledge base]\n{rag_failures}\n\n"
        f"[LIVE REDDIT COMMUNITY DATA — real user pain points]\n{tool_result}\n\n"
        "Using BOTH the failure patterns above AND the Reddit data, give a 2-3 sentence critique covering:\n"
        "- Which known startup failure pattern (from the knowledge base) does this idea risk repeating?\n"
        "- How validated is this problem from Reddit data? (cite actual posts if found)\n"
        "- Top 2 risks with specific mitigation strategies\n"
        "End with exactly: [SCORE: X/10]"
    )
    raw    = call_ai(prompt, fast)
    result = _parse_critique(raw, "Risk")
    result.update({
        "tool_name": "Reddit API (PRAW)",
        "tool_query": query,
        "tool_result_snippet": snippet,
        "rag_used": True,
    })
    return result


# ── PHASE 3: CEO Revision ─────────────────────────────────────────────────────

def ceo_revise(idea: str, prev_proposal: str, critiques: list,
               round_num: int, fast: bool = False) -> dict:
    critique_text = "\n".join(
        f"- {c['agent']} (score {c['score']}/10): {c['content']}"
        for c in critiques
    )
    prompt = (
        f"You are the CEO revising your startup proposal (round {round_num}).\n"
        f"Idea: '{idea}'\nPrevious proposal: '{prev_proposal}'\n\n"
        f"Team critique (grounded in real data):\n{critique_text}\n\n"
        "Write a revised proposal (3-4 sentences of prose) that directly addresses each concern. "
        "Reference specific improvements to the financial model, tech approach, or risk strategy."
    )
    content = call_ai(prompt, fast)
    return {
        "agent": "CEO",
        "tool_name": None,
        "tool_query": None,
        "tool_result_snippet": None,
        "content": content,
    }


# ── PHASE 4: Synthesis ────────────────────────────────────────────────────────

def synthesize(idea: str, final_proposal: str, critiques: list,
               fast: bool = False) -> dict:
    """
    IMPROVED PROMPT:
    - Executive Summary: 1 paragraph + 3-4 bullet points
    - Technology Stack: markdown table (Layer | Technology | Purpose | Cost)
      using REAL choices from dev/finance critiques — not generic
    - Financial Model: 1 paragraph + key numbers as bullets
    - Marketing Strategy: 1 paragraph + channel bullets
    - Risk Assessment: 1 paragraph + risk bullets with mitigations
    """
    critique_text = "\n".join(
        f"- {c['agent']} (grounded in {c.get('tool_name','LLM')}, score {c.get('score','?')}/10):\n  {c['content']}"
        for c in critiques
    )

    # Pull dev critique content specifically so LLM can reference real tech choices
    dev_content  = next((c['content'] for c in critiques if c['agent'] == 'Developer'), '')
    fin_content  = next((c['content'] for c in critiques if c['agent'] == 'Finance'), '')
    risk_content = next((c['content'] for c in critiques if c['agent'] == 'Risk'), '')
    mkt_content  = next((c['content'] for c in critiques if c['agent'] == 'Marketing'), '')

    prompt = f"""You are the Chief Strategy Officer synthesizing a final business plan for: '{idea}'.

Final CEO proposal: '{final_proposal}'

Agent critiques (grounded in real live data):
{critique_text}

Write a DETAILED, STRUCTURED business plan with EXACTLY these 5 sections.
Use the exact section headers below (with ### prefix).
Each section must use the format described.

### Executive Summary
Write 1 solid paragraph (4-5 sentences) summarising the opportunity, market, and strategy.
Then add 3-4 bullet points highlighting key strengths found in agent research.
Cite specific data points from the critiques (competitor names, trend numbers, Reddit findings).

### Technology Stack
Based on the Developer Agent critique: '{dev_content[:400]}'
Output a markdown table with EXACTLY these columns: Layer | Technology | Purpose | Cost
Rows must reflect the ACTUAL tech choices appropriate for '{idea}' — not generic tools.
Choose the right framework, database, frontend, and infra based on what the Dev Agent found.
After the table, write 1-2 sentences explaining the architectural decision.

### Financial Model
Based on the Finance Agent critique: '{fin_content[:300]}'
Write 1 paragraph on revenue model and pricing strategy (cite real trend data if available).
Then add bullet points for: Revenue streams, Cost structure, Break-even estimate, Key metric.

### Marketing Strategy
Based on the Marketing Agent critique: '{mkt_content[:300]}'
Write 1 paragraph on positioning and GTM strategy (name real competitors found).
Then add bullet points for: Primary channel, Secondary channel, Differentiation, Target segment.

### Risk Assessment
Based on the Risk Agent critique: '{risk_content[:300]}'
Write 1 paragraph identifying the top failure pattern this idea risks.
Then add bullet points for each risk: Risk description → Mitigation strategy.

IMPORTANT RULES:
- Technology Stack section MUST contain a markdown table (| col | col | col | col |)
- All sections must reference specific data from the agent critiques
- Do NOT write generic filler — every sentence must be grounded in the research
- Do NOT repeat the section header inside the section body
"""

    raw = call_ai(prompt, fast)
    return _parse_plan(raw)


# ── DEPLOY: Generate Boilerplate Codebase ────────────────────────────────────

def _extract_tech_table(tech_stack_text: str) -> str:
    """
    Extract the markdown table from the Technology Stack section if it exists.
    If not found, build a simple table from keyword extraction.
    Returns a markdown table string.
    """
    # Check if the LLM produced a proper markdown table
    lines = tech_stack_text.strip().splitlines()
    table_lines = [l for l in lines if '|' in l]

    if len(table_lines) >= 3:
        # Has a real table — return it as-is
        return "\n".join(table_lines)

    # No table found — build one from common tech keywords in the text
    text_lower = tech_stack_text.lower()

    rows = []

    # Backend framework
    if 'fastapi' in text_lower:
        rows.append('| Backend | FastAPI + Uvicorn | REST API + SSE streaming | Free |')
    elif 'django' in text_lower:
        rows.append('| Backend | Django + DRF | REST API framework | Free |')
    elif 'flask' in text_lower:
        rows.append('| Backend | Flask | Lightweight API server | Free |')
    elif 'express' in text_lower or 'node' in text_lower:
        rows.append('| Backend | Node.js + Express | API server | Free |')
    else:
        rows.append('| Backend | FastAPI + Uvicorn | REST API + SSE streaming | Free |')

    # Frontend
    if 'next' in text_lower:
        rows.append('| Frontend | Next.js + React | SSR web application | Free |')
    elif 'react' in text_lower:
        rows.append('| Frontend | React + Vite | SPA frontend | Free |')
    elif 'vue' in text_lower:
        rows.append('| Frontend | Vue.js | Progressive web UI | Free |')
    elif 'flutter' in text_lower or 'dart' in text_lower:
        rows.append('| Frontend | Flutter | Cross-platform mobile + web | Free |')
    elif 'kotlin' in text_lower:
        rows.append('| Frontend | Kotlin + Jetpack Compose | Android native app | Free |')
    elif 'swift' in text_lower:
        rows.append('| Frontend | Swift + SwiftUI | iOS native app | Free |')
    else:
        rows.append('| Frontend | React + Vite | SPA frontend | Free |')

    # Database
    if 'postgres' in text_lower or 'postgresql' in text_lower:
        rows.append('| Database | PostgreSQL | Relational data store | Free |')
    elif 'mongodb' in text_lower or 'mongo' in text_lower:
        rows.append('| Database | MongoDB | Document database | Free tier |')
    elif 'mysql' in text_lower:
        rows.append('| Database | MySQL | Relational database | Free |')
    elif 'sqlite' in text_lower:
        rows.append('| Database | SQLite | Lightweight local DB | Free |')
    elif 'redis' in text_lower:
        rows.append('| Database | Redis + PostgreSQL | Cache + persistent store | Free |')
    else:
        rows.append('| Database | PostgreSQL | Relational data store | Free |')

    # Auth
    if 'auth0' in text_lower:
        rows.append('| Auth | Auth0 | Managed authentication | Free tier |')
    elif 'jwt' in text_lower or 'jose' in text_lower:
        rows.append('| Auth | JWT (python-jose) | Token-based auth | Free |')
    else:
        rows.append('| Auth | JWT + bcrypt | Stateless authentication | Free |')

    # AI / ML if relevant
    if 'openai' in text_lower or 'gpt' in text_lower:
        rows.append('| LLM | OpenAI GPT-4o | AI features | API cost |')
    elif 'anthropic' in text_lower or 'claude' in text_lower:
        rows.append('| LLM | Anthropic Claude | AI reasoning | API cost |')
    elif 'huggingface' in text_lower or 'qwen' in text_lower:
        rows.append('| LLM | HuggingFace Inference | Open-source LLM | Free tier |')

    # Infrastructure
    if 'kubernetes' in text_lower or 'k8s' in text_lower:
        rows.append('| Infra | Kubernetes + Docker | Container orchestration | Free |')
    else:
        rows.append('| Infra | Docker + Docker Compose | Containerization | Free |')

    # Payments if SaaS
    if 'stripe' in text_lower:
        rows.append('| Payments | Stripe | Subscription billing | 2.9% + 30¢ |')

    # CI/CD
    rows.append('| CI/CD | GitHub Actions | Automated testing + deploy | Free |')

    header = "| Layer | Technology | Purpose | Cost |\n|---|---|---|---|"
    return header + "\n" + "\n".join(rows)


def generate_boilerplate(idea: str, plan: dict) -> dict:
    """
    Generates a rich, startup-specific codebase based on the validated plan.
    Returns {filename: content} ready to push to GitHub.

    Tech stack table is built from the REAL Technology Stack section produced
    by the synthesize() LLM call — not hardcoded.
    """
    tech_stack_text = plan.get("Technology Stack", "")
    exec_summary    = plan.get("Executive Summary", "")
    financial_model = plan.get("Financial Model", "")
    marketing       = plan.get("Marketing Strategy", "")
    risk            = plan.get("Risk Assessment", "")

    # Build the real tech table from LLM output (not hardcoded)
    tech_table = _extract_tech_table(tech_stack_text)

    # Derive project name from idea
    project_name = "-".join(idea.lower().split()[:4])
    project_name = re.sub(r"[^a-z0-9\-]", "", project_name).strip("-")

    # ── 1. README.md ──────────────────────────────────────────────────────
    # First sentence of exec summary as tagline
    tagline = ""
    if exec_summary:
        first_sentence = exec_summary.split('.')[0].strip()
        tagline = first_sentence[:200] if first_sentence else exec_summary[:200]

    readme = f"""# {idea}

> {tagline or 'An AI-validated startup built with FoundrAI 2.0.'}

[![FoundrAI](https://img.shields.io/badge/Generated%20by-FoundrAI%202.0-6366f1?style=flat-square)](https://github.com/foundr-ai)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Validated](https://img.shields.io/badge/AI%20Consensus-Validated-22c55e?style=flat-square)](https://github.com/foundr-ai)

---

## 📋 Executive Summary

{exec_summary if exec_summary else '_See business plan PDF for full summary._'}

---

## 🏗️ Tech Stack

{tech_stack_text if tech_stack_text else ''}

{tech_table}

---

## 💰 Financial Model

{financial_model if financial_model else '_See Financial Model section of business plan._'}

---

## 📣 Marketing Strategy

{marketing if marketing else '_See Marketing Strategy section of business plan._'}

---

## ⚠️ Risk Assessment

{risk if risk else '_See Risk Assessment section of business plan._'}

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 1. Clone and configure
```bash
git clone https://github.com/your-org/{project_name}
cd {project_name}
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run with Docker (recommended)
```bash
docker compose up --build
```

### 3. Run locally
```bash
# Backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install && npm run dev
```

### 4. API access
- REST API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

---

## 📁 Project Structure

```
{project_name}/
├── app/
│   └── main.py          # FastAPI entry point with core routes
├── frontend/            # Web frontend
├── docker-compose.yml   # Service definitions (API + DB)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── foundrai.json        # FoundrAI validation manifest
└── README.md
```

---

## 🤖 Validated by FoundrAI 2.0

This project was autonomously validated by a multi-agent AI consensus system:

| Agent | Tool Used | Finding |
|---|---|---|
| 🧠 CEO Agent | Tavily Web Search | Live market research & competitor landscape |
| ⚡ Dev Agent | GitHub Search API | Tech stack validation & community support |
| 📈 Finance Agent | Google Trends (PyTrends) | Market demand validation |
| 🌐 Marketing Agent | Tavily Competitor Intel | Competitor pricing & GTM strategy |
| ⚠️ Risk Agent | Reddit (PRAW) + RAG | Community pain points & failure patterns |

*Built with [FoundrAI 2.0](https://github.com/foundr-ai) — Autonomous Business Validation Engine*
"""

    # ── 2. docker-compose.yml ──────────────────────────────────────────────
    docker_compose = f"""version: '3.9'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {project_name}_api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${{DATABASE_URL}}
      - SECRET_KEY=${{SECRET_KEY}}
      - ENVIRONMENT=production
    env_file:
      - .env
    depends_on:
      - db
    restart: unless-stopped
    volumes:
      - ./app:/app/app

  db:
    image: postgres:15-alpine
    container_name: {project_name}_db
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: {project_name.replace('-','_')}
      POSTGRES_USER: ${{POSTGRES_USER:-appuser}}
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD}}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${{POSTGRES_USER:-appuser}}"]
      interval: 10s
      timeout: 5s
      retries: 5

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: {project_name}_frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
"""

    # ── 3. .env.example ────────────────────────────────────────────────────
    env_example = f"""# {idea} — Environment Variables
# Copy this file to .env and fill in your values

# ── Database ──────────────────────────────────────────────────────────────
DATABASE_URL=postgresql://appuser:yourpassword@db:5432/{project_name.replace('-','_')}
POSTGRES_USER=appuser
POSTGRES_PASSWORD=change_me_in_production

# ── App Security ──────────────────────────────────────────────────────────
SECRET_KEY=your-256-bit-secret-key-here
ENVIRONMENT=development       # development | production

# ── External APIs ─────────────────────────────────────────────────────────
# Tavily — live web search (https://tavily.com)
TAVILY_API_KEY=tvly-your-key-here

# HuggingFace — LLM inference (https://huggingface.co)
HF_TOKEN=hf_your_token_here

# GitHub — autonomous deployment (https://github.com/settings/tokens)
GITHUB_TOKEN=ghp_your_token_here
GITHUB_ORG=           # leave blank to use personal account

# OpenAI — optional fallback LLM
OPENAI_API_KEY=sk-your-key-here

# ── Frontend ──────────────────────────────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000
"""

    # ── 4. app/main.py ─────────────────────────────────────────────────────
    # Build a first-sentence tagline cleanly for the description field
    description = tagline.replace('"', "'") if tagline else "AI-validated startup API"

    main_py = f'''"""
{idea} — FastAPI Backend
Generated by FoundrAI 2.0

Tech Stack: {tech_stack_text[:120] if tech_stack_text else 'FastAPI, PostgreSQL'}
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(
    title="{idea}",
    description="{description[:120]}",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    name: str
    password: str


class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Health check and project info."""
    return {{
        "project": "{idea}",
        "version": "0.1.0",
        "status": "running",
        "generated_by": "FoundrAI 2.0",
    }}


@app.get("/health")
async def health():
    """Kubernetes/Docker health probe."""
    return {{"status": "ok"}}


@app.post("/users", status_code=201)
async def create_user(user: UserCreate):
    """Register a new user. TODO: connect to PostgreSQL."""
    return {{
        "id": 1,
        "email": user.email,
        "name": user.name,
        "message": "User created successfully",
    }}


@app.get("/users/{{user_id}}")
async def get_user(user_id: int):
    """Fetch a user by ID."""
    if user_id != 1:
        raise HTTPException(status_code=404, detail="User not found")
    return {{"id": user_id, "email": "demo@example.com", "name": "Demo User"}}


@app.post("/items", status_code=201)
async def create_item(item: ItemCreate):
    """
    Core business entity endpoint.
    Customise to match your domain:
    food app → POST /meals, SaaS → POST /projects, etc.
    """
    return {{
        "id": 1,
        "title": item.title,
        "description": item.description,
        "status": "created",
    }}


@app.get("/items")
async def list_items(skip: int = 0, limit: int = 20):
    """List all items with pagination."""
    return {{"items": [], "total": 0, "skip": skip, "limit": limit}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''

    # ── 5. requirements.txt ────────────────────────────────────────────────
    requirements = """fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic>=2.0.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
httpx>=0.27.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9
"""

    # ── 6. foundrai.json manifest ──────────────────────────────────────────
    manifest = _json.dumps({
        "generated_by": "FoundrAI 2.0",
        "idea": idea,
        "tech_stack_raw": tech_stack_text[:500] if tech_stack_text else "",
        "consensus_validated": True,
        "plan_sections": list(plan.keys()),
    }, indent=2)

    return {
        "README.md":          readme,
        "docker-compose.yml": docker_compose,
        ".env.example":       env_example,
        "app/main.py":        main_py,
        "requirements.txt":   requirements,
        "foundrai.json":      manifest,
    }


# ── MONITOR: Auto-Strategy Update ────────────────────────────────────────────

def generate_monitor_update(idea: str, new_market_data: str) -> str:
    """
    Given new market signals, generate a revised Marketing Strategy section.
    Used by the Auto-Monitor daemon (and the Fast-Forward demo button).
    """
    prompt = (
        f"You are a startup strategist responding to NEW market intelligence.\n"
        f"Startup idea: '{idea}'\n\n"
        f"[NEW MARKET SIGNALS DETECTED]\n{new_market_data}\n\n"
        "Based on these new signals, write a revised Marketing Strategy (2-3 sentences) that:\n"
        "- Directly responds to the new competitor or trend detected\n"
        "- Adjusts the growth channel or positioning accordingly\n"
        "- Is concrete and actionable\n"
        "Start your response with '⚡ UPDATED:'"
    )
    return call_ai(prompt, fast=True)