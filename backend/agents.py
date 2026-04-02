import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
# InferenceClient handles API routing natively
client = InferenceClient(api_key=HF_TOKEN)

def call_hf_api(prompt: str) -> str:
    if not HF_TOKEN:
        # Fallback for local testing if token is missing
        return f"[MOCK] This is a mock response because HF_TOKEN was not found. Prompt was: {prompt[:30]}..."

    try:
        # Qwen2.5-72B-Instruct is a highly capable and currently supported free-tier model
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct",
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling AI: {str(e)}"

# Agent definitions
def run_ceo_agent(idea: str) -> str:
    prompt = f"You are the CEO of a new startup. The initial idea is: '{idea}'. Briefly outline the core vision, target audience, and the overall roadmap in 3 bullet points."
    return call_hf_api(prompt)

def run_dev_agent(idea: str, ceo_output: str) -> str:
    prompt = f"You are the Lead Developer. The startup idea is: '{idea}'. The CEO's vision is: '{ceo_output}'. Propose the optimal technology stack and 3 core features for the MVP."
    return call_hf_api(prompt)

def run_marketing_agent(idea: str, ceo_output: str) -> str:
    prompt = f"You are the Chief Marketing Officer. The startup idea is: '{idea}'. The CEO's vision is: '{ceo_output}'. Create a 2-sentence positioning statement and name one key marketing channel."
    return call_hf_api(prompt)

def run_finance_agent(idea: str, ceo_output: str, dev_output: str) -> str:
    prompt = f"You are the CFO. Idea: '{idea}'. Vision: '{ceo_output}'. Tech: '{dev_output}'. Briefly estimate the primary costs (development & marketing) and state the basic revenue model."
    return call_hf_api(prompt)
