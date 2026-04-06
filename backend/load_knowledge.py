"""
FoundrAI 2.0 — Knowledge Base Loader
Runs ONCE on startup. Loads all knowledge files into ChromaDB.
If the collection already exists and is populated, skips loading.
"""

import os
import time
import requests
from dotenv import load_dotenv
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings

load_dotenv()

CHROMA_PATH = "/app/chroma_data"
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
COLLECTION_NAME = "yc_knowledge"
CHUNK_SIZE = 800        # characters per chunk
CHUNK_OVERLAP = 100     # overlap between chunks

KNOWLEDGE_FILES = [
    ("pg_essays.txt",         "Paul Graham Essays"),
    ("yc_advice.txt",         "Y Combinator Advice"),
    ("pitch_decks.txt",       "Successful Pitch Decks"),
    ("failure_postmortems.txt", "Startup Failure Post-Mortems"),
]

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
                
                print(f"[RAG] HF API waiting (status {resp.status_code}): {resp.text[:100]}... retrying in 5s.")
            except Exception as e:
                print(f"[RAG] HF API network error: {e}... retrying in 5s.")
            time.sleep(5)
        
        print("[RAG] ERROR: HF API failed after retries. Returning empty vectors.")
        return [[0.0] * 384 for _ in input]


def chunk_text(text: str, source: str) -> list[dict]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        if chunk.strip():
            chunks.append({
                "id": f"{source}_{idx}",
                "text": chunk.strip(),
                "source": source,
            })
        start = end - CHUNK_OVERLAP
        idx += 1
    return chunks


def load_yc_knowledge():
    """Load all knowledge files into ChromaDB using robust HuggingFace API embeddings."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token or hf_token.startswith("your_"):
        print("[RAG] WARNING: HF_TOKEN not set. Embeddings API requires it.")
    
    ef = RobustHFEmbeddingFunction(api_key=hf_token)

    # Check if already loaded
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        collection = client.get_collection(COLLECTION_NAME, embedding_function=ef)
        count = collection.count()
        if count > 0:
            print(f"[RAG] Knowledge base already loaded ({count} chunks). Skipping.")
            return
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(COLLECTION_NAME, embedding_function=ef)

    all_ids, all_docs, all_metas = [], [], []

    for filename, source_label in KNOWLEDGE_FILES:
        path = os.path.join(KNOWLEDGE_DIR, filename)
        if not os.path.exists(path):
            print(f"[RAG] Warning: {filename} not found, skipping.")
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = chunk_text(text, source_label)
        print(f"[RAG] Loaded {filename} → {len(chunks)} chunks")
        for c in chunks:
            all_ids.append(c["id"])
            all_docs.append(c["text"])
            all_metas.append({"source": c["source"]})

    # Batch upsert in groups of 100 (ChromaDB default batch limit)
    batch_size = 100
    for i in range(0, len(all_ids), batch_size):
        collection.add(
            ids=all_ids[i:i+batch_size],
            documents=all_docs[i:i+batch_size],
            metadatas=all_metas[i:i+batch_size],
        )

    print(f"[RAG] Knowledge base ready: {len(all_ids)} total chunks loaded into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    load_yc_knowledge()
