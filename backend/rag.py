"""
FoundrAI 2.0 — RAG Query Module
Queries the ChromaDB knowledge base for relevant startup wisdom.
"""

import os
import time
import requests
from dotenv import load_dotenv
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings

load_dotenv()

CHROMA_PATH = "/app/chroma_data"
COLLECTION_NAME = "yc_knowledge"

_client = None
_collection = None


class RobustHFEmbeddingFunction(EmbeddingFunction):
    """Custom wrapper for HF Inference API to safely handle cold-start and rate limits."""
    def __init__(self, api_key: str):
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def __call__(self, input: Documents) -> Embeddings:
        retries = 8
        for i in range(retries):
            try:
                resp = requests.post(self.api_url, headers=self.headers, json={"inputs": input, "options": {"wait_for_model": True}}, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    # Expecting a list of lists of floats
                    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                        return data
            except Exception:
                pass
            time.sleep(5)
        return [[0.0] * 384 for _ in input]


def _get_collection():
    global _client, _collection
    if _collection is None:
        try:
            _client = chromadb.PersistentClient(path=CHROMA_PATH)
            hf_token = os.getenv("HF_TOKEN")
            ef = RobustHFEmbeddingFunction(api_key=hf_token)
            _collection = _client.get_collection(COLLECTION_NAME, embedding_function=ef)
        except Exception as e:
            print(f"[RAG] Warning: Could not connect to ChromaDB: {e}")
            _collection = None
    return _collection


def query_knowledge(query: str, n_results: int = 3) -> str:
    """
    Query the YC/PG knowledge base for relevant context.
    Returns a formatted string of the top-N results with source labels.
    Falls back gracefully if ChromaDB is not available.
    """
    collection = _get_collection()
    if collection is None:
        return "[RAG UNAVAILABLE] ChromaDB not loaded. CEO will proceed without knowledge base context."

    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count()),
        )
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        if not docs:
            return "[RAG] No relevant knowledge found for this query."

        formatted = []
        for doc, meta in zip(docs, metas):
            source = meta.get("source", "Unknown")
            formatted.append(f"[{source}]\n{doc.strip()}")

        return "\n\n---\n\n".join(formatted)

    except Exception as e:
        return f"[RAG ERROR] Query failed: {str(e)}"


def query_for_idea(idea: str) -> str:
    """Convenience: query the knowledge base with a startup-idea-aware prompt."""
    query = f"startup positioning strategy and market validation for: {idea}"
    return query_knowledge(query, n_results=3)


def query_for_risks(idea: str) -> str:
    """Query specifically for failure patterns relevant to the idea."""
    query = f"startup failure reasons and risks for: {idea}"
    return query_knowledge(query, n_results=2)


def query_for_pitch(idea: str) -> str:
    """Query for pitch deck wisdom relevant to the idea."""
    query = f"pitch deck strategy and investor positioning for: {idea}"
    return query_knowledge(query, n_results=2)
