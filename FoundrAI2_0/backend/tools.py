"""
FoundrAI 2.0 — LangChain @tool definitions
Each tool wraps a real external API with graceful fallback if the key is missing.
"""

import os
import re
import json
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")


# ── CEO Tool: Live Startup Research via Tavily ────────────────────────────────

@tool
def search_recent_startups(query: str) -> str:
    """Search for recent startups and market trends for a given idea."""
    if not TAVILY_KEY or TAVILY_KEY.startswith("your_"):
        return "[FALLBACK] Tavily key not set. Proceeding without live startup data."
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_KEY)
        results = client.search(query, max_results=3)
        snippets = []
        for r in results.get("results", []):
            snippets.append(f"• {r.get('title', '')}: {r.get('content', '')[:150]}")
        return "\n".join(snippets[:3]) if snippets else "No results found."
    except Exception as e:
        return f"[TOOL ERROR] Tavily search failed: {str(e)}"


# ── Marketing Tool: Competitor Intelligence via Tavily ────────────────────────

@tool
def search_competitors(query: str) -> str:
    """Search for exact competitors, their pricing, and weaknesses."""
    if not TAVILY_KEY or TAVILY_KEY.startswith("your_"):
        return "[FALLBACK] Tavily key not set. Proceeding without competitor intelligence."
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_KEY)
        results = client.search(f"competitors pricing alternatives {query}", max_results=3)
        snippets = []
        for r in results.get("results", []):
            snippets.append(f"• {r.get('title', '')}: {r.get('content', '')[:150]}")
        return "\n".join(snippets[:3]) if snippets else "No competitor data found."
    except Exception as e:
        return f"[TOOL ERROR] Tavily competitor search failed: {str(e)}"


# ── Risk Tool: Social Proof via Demo Reddit Posts ────────────────────────────

REDDIT_DEMO_PATH = os.path.join(os.path.dirname(__file__), "knowledge", "reddit_demo.txt")

def _load_reddit_posts() -> list[dict]:
    """Parse reddit_demo.txt into a list of post dicts."""
    posts = []
    if not os.path.exists(REDDIT_DEMO_PATH):
        return posts
    with open(REDDIT_DEMO_PATH, "r", encoding="utf-8") as f:
        raw = f.read()
    # Split on the separator
    blocks = [b.strip() for b in raw.split("---") if b.strip()]
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        header = lines[0]          # "[r/sub] | upvotes | Title"
        body   = "\n".join(lines[1:]).strip()
        # Parse header
        parts = [p.strip() for p in header.split("|")]
        subreddit = parts[0].strip("[] ") if len(parts) > 0 else "r/startups"
        title     = parts[2] if len(parts) > 2 else header
        posts.append({"subreddit": subreddit, "title": title, "body": body})
    return posts


@tool
def search_reddit_pain_points(keyword: str) -> str:
    """
    Search curated Reddit community posts for real user pain points about a problem space.
    Uses a local demo dataset of 30 real-style community discussions.
    """
    posts = _load_reddit_posts()
    if not posts:
        return "[FALLBACK] Reddit demo file not found."

    keywords = keyword.lower().split()

    def score(post):
        text = (post["title"] + " " + post["body"]).lower()
        return sum(1 for kw in keywords if kw in text)

    ranked = sorted(posts, key=score, reverse=True)
    top    = [p for p in ranked if score(p) > 0][:5]

    if not top:
        # Fall back to returning top 3 most general posts
        top = ranked[:3]

    lines = []
    for p in top:
        snippet = p["body"][:180].replace("\n", " ") + "..."
        lines.append(f"• {p['subreddit']}: \"{p['title']}\" — {snippet}")

    return "\n".join(lines)


# ── Finance Tool: Market Demand via PyTrends ──────────────────────────────────

@tool
def get_google_trends(keyword: str) -> str:
    """Get Google Trends data to validate market demand over the past 12 months."""
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(5, 10))
        # Use only first 2 words to avoid keyword errors
        kw = " ".join(keyword.split()[:3])
        pytrends.build_payload([kw], timeframe="today 12-m")
        df = pytrends.interest_over_time()
        if df.empty:
            return f"No trend data found for '{kw}'."
        avg_interest = int(df[kw].mean())
        peak         = int(df[kw].max())
        recent       = int(df[kw].iloc[-1])
        trend_dir    = "📈 Growing" if df[kw].iloc[-1] > df[kw].iloc[0] else "📉 Declining"
        return (
            f"Keyword: '{kw}' | Trend: {trend_dir}\n"
            f"Avg interest (0-100): {avg_interest} | Peak: {peak} | Last data point: {recent}"
        )
    except Exception as e:
        return f"[TOOL ERROR] PyTrends failed: {str(e)}"


# ── Developer Tool: GitHub Stack Validator ────────────────────────────────────

@tool
def search_github_repos(query: str) -> str:
    """Search GitHub for similar open-source projects to validate tech stack and community support."""
    try:
        url      = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
        response = requests.get(url, timeout=8)
        response.raise_for_status()

        repos = response.json().get("items", [])[:4]
        if not repos:
            return "No similar GitHub repositories found."

        lines = []
        for repo in repos:
            lang  = repo.get("language") or "Unknown"
            stars = repo.get("stargazers_count", 0)
            desc  = (repo.get("description") or "")[:100]
            lines.append(f"• {repo['full_name']} [{lang}] ⭐{stars:,} — {desc}")

        return "\n".join(lines)
    except Exception as e:
        return f"[TOOL ERROR] GitHub search failed: {str(e)}"


# ── Developer Agent: Autonomous GitHub Deployment ────────────────────────────

@tool
def deploy_to_github(repo_name: str, files_json: str) -> str:
    """
    Create a private GitHub repo named after the startup and push boilerplate files
    in a single commit. files_json is a JSON string of {filename: content}.
    Returns the repo HTML URL on success.
    """
    github_token = os.getenv("GITHUB_TOKEN", "")
    if not github_token or github_token.startswith("your_"):
        return "[FALLBACK] GITHUB_TOKEN not set. Cannot deploy. Set GITHUB_TOKEN in .env."
    try:
        from github import Github
        import base64

        files = json.loads(files_json)
        g    = Github(github_token)
        user = g.get_user()

        # Sanitize repo name: lowercase, no spaces, max 100 chars
        safe_name = re.sub(r"[^a-zA-Z0-9\-]", "-", repo_name.lower()).strip("-")[:80]
        safe_name = re.sub(r"-+", "-", safe_name)  # collapse multiple dashes

        # Create private repo
        repo = user.create_repo(
            safe_name,
            private=True,
            description="Generated by FoundrAI 2.0 — AI-validated startup codebase",
            auto_init=False,
        )

        # Push all files in one commit using Git Trees API (single commit)
        blobs = []
        for filename, content in files.items():
            blob = repo.create_git_blob(content, "utf-8")
            blobs.append({
                "path": filename,
                "mode": "100644",
                "type": "blob",
                "sha": blob.sha,
            })

        tree    = repo.create_git_tree(blobs)
        commit  = repo.create_git_commit(
            message="🤖 Initial commit by FoundrAI 2.0",
            tree=tree,
            parents=[],
        )
        repo.create_git_ref("refs/heads/main", commit.sha)

        return repo.html_url

    except Exception as e:
        return f"[TOOL ERROR] GitHub deployment failed: {str(e)}"
