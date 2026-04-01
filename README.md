# FoundrAI: Multi-Agent AI Startup Simulator

An interactive Multi-Agent AI Startup Simulator that transforms any idea into a comprehensive business plan. Powered by FastAPI, React, and Hugging Face, it features 4 autonomous agents (CEO, Dev, Marketing, Finance) collaborating in real-time. Watch the agents work sequentially through a premium, glassmorphic UI with live streaming animations.

## 🚀 Getting Started

The easiest way to run the application is using Docker!

### Requirements
- [Docker](https://www.docker.com/) & Docker Compose
- A free [Hugging Face Inference API Token](https://huggingface.co/settings/tokens)

### Running with Docker

1. **Add your Hugging Face Token**
   Open `backend/.env` (create it if it doesn't exist) and paste your free token:
   ```env
   HF_TOKEN=hf_your_token_here
   ```
   *(Note: The `.env` file is git-ignored, to ensure your token is not accidentally pushed!)*

2. **Start the containers**
   ```bash
   docker-compose up --build -d
   ```

3. **Open the Application**
   Navigate to [http://localhost:5173](http://localhost:5173) in your browser.

---

### Manual Setup (Without Docker)

If you prefer to run the development servers directly:

**Backend (Terminal 1):**
```bash
cd backend
# Create a virtual environment (recommended)
python -m venv venv
# Activate it (Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Basic Features to Test

Once the application is running, give these features a spin:

1. **The Core UI**: Verify the responsive, glassmorphic design and the initial empty states of the 4 agents.
2. **Sequential Agent Handoff**: 
   - Type a startup concept like *"A subscription box for rare indoor plants"* and hit **"Initiate Agents"**.
   - You should see the **CEO** card transition to 'Thinking...' first.
   - Once the CEO outputs the vision, the **Lead Developer** will take over automatically.
   - Finally, the **CMO** and **CFO** should spin up concurrently based on the Developer's output.
3. **Live Streaming (SSE)**: Ensure that the UI updates dynamically and naturally without the page freezing or requiring a refresh. Observe the glowing active states!
