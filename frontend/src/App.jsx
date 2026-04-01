import React, { useState, useEffect, useRef } from 'react';
import { Bot, Terminal, Presentation, DollarSign, Send, Lightbulb, Activity, CheckCircle2 } from 'lucide-react';
import './index.css';

// Agent configuration map for icons and titles
const AGENTS_CONFIG = {
  "CEO": { icon: <Lightbulb size={20} />, title: "CEO" },
  "Developer": { icon: <Terminal size={20} />, title: "Lead Developer" },
  "Marketing": { icon: <Presentation size={20} />, title: "CMO" },
  "Finance": { icon: <DollarSign size={20} />, title: "CFO" }
};

// Formats the markdown text into basic HTML (paragraphs and bold)
const formatText = (text) => {
  if (!text) return null;
  const parts = text.split('\n').filter(p => p.trim() !== '');
  return parts.map((part, i) => {
    // Replace markdown bold **text** with <strong>text</strong> safely
    const formattedHtml = part.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\[INST\]/g, '')
      .replace(/\[\/INST\]/g, '');
    return <p key={i} dangerouslySetInnerHTML={{ __html: formattedHtml }} />;
  });
};

const AgentCard = ({ id, status, output }) => {
  const { icon, title } = AGENTS_CONFIG[id];

  return (
    <div className={`agent-card ${status}`}>
      {status === 'working' && <div className="flow-line active" />}

      <div className="agent-header">
        <div className="agent-icon">
          {icon}
        </div>
        <div className="agent-title">{title}</div>
        <div className="agent-status">
          {status === 'idle' ? 'Awaiting Input' :
            status === 'working' ? 'Thinking...' : 'Complete'}
        </div>
      </div>

      <div className={`agent-content ${output ? 'rendered' : ''}`}>
        {status === 'idle' && (
          <div style={{ opacity: 0.5, textAlign: 'center', marginTop: '20px' }}>
            <Bot size={32} opacity={0.5} style={{ display: 'block', margin: '0 auto 10px' }} />
            Standing by...
          </div>
        )}

        {status === 'working' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '20px', color: 'var(--accent-blue)' }}>
            <Activity className="spinner" size={20} />
            <span style={{ animation: 'blink 1.5s infinite' }}>Analyzing context and drafting...</span>
          </div>
        )}

        {status === 'complete' && output && (
          <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
            {formatText(output)}
          </div>
        )}
      </div>
    </div>
  );
};

export default function App() {
  const [idea, setIdea] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [agents, setAgents] = useState({
    "CEO": { status: "idle", output: "" },
    "Developer": { status: "idle", output: "" },
    "Marketing": { status: "idle", output: "" },
    "Finance": { status: "idle", output: "" }
  });
  const bottomRef = useRef(null);

  const simulateMVP = async () => {
    if (!idea.trim() || isRunning) return;

    // Reset state
    setIsRunning(true);
    setAgents({
      "CEO": { status: "idle", output: "" },
      "Developer": { status: "idle", output: "" },
      "Marketing": { status: "idle", output: "" },
      "Finance": { status: "idle", output: "" }
    });

    try {
      const response = await fetch("http://localhost:8000/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.agent === "System") {
                if (data.status === "done") setIsRunning(false);
                continue;
              }

              setAgents(prev => ({
                ...prev,
                [data.agent]: {
                  status: data.status,
                  output: data.output || prev[data.agent].output
                }
              }));

            } catch (e) { console.error("Parse error", e); }
          }
        }
      }
    } catch (err) {
      console.error("Simulation failed", err);
      setIsRunning(false);
    }
  };

  useEffect(() => {
    if (isRunning) {
      setTimeout(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, [agents, isRunning]);

  return (
    <div className="app-container">
      <header className="header">
        <h1 className="title-gradient">MultiAgent AI Startup</h1>
        <p className="subtitle">Watch an entire AI team turn your concept into a startup</p>
      </header>

      <main>
        <div className="input-section">
          <textarea
            className="idea-input"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder="Describe your startup idea (e.g., 'An AI-powered app that generates personalized diets based on blood tests')..."
            disabled={isRunning}
          />
          <button
            className="simulate-btn"
            onClick={simulateMVP}
            disabled={!idea.trim() || isRunning}
          >
            {isRunning ? (
              <><Activity size={18} className="spinner" /> Generating Startup...</>
            ) : (
              <>Initiate Agents <Send size={18} /></>
            )}
          </button>
        </div>

        <div className="agents-grid">
          <AgentCard id="CEO" {...agents["CEO"]} />
          <AgentCard id="Developer" {...agents["Developer"]} />
          <AgentCard id="Marketing" {...agents["Marketing"]} />
          <AgentCard id="Finance" {...agents["Finance"]} />
        </div>

        <div ref={bottomRef} style={{ height: '40px' }} />
      </main>
    </div>
  );
}
