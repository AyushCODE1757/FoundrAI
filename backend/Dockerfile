FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and knowledge files
COPY . .

# Using HuggingFace Inference API, so no local model downloads needed.
EXPOSE 8000

# On startup: load knowledge base (idempotent) then start API server
CMD ["sh", "-c", "python load_knowledge.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
