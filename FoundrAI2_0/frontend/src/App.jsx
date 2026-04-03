import React, { useState, useRef, useCallback } from 'react';
import {
  Lightbulb, Code2, DollarSign, Megaphone, ShieldAlert,
  Sparkles, Send, Zap, RotateCcw, CheckCircle2, AlertTriangle,
  Download, Activity, Users, MessageSquare
} from 'lucide-react';
import './index.css';

// ── Agent config ────────────────────────────────────────────────────────────
const AGENTS = {
  CEO:        { label: 'CEO',        Icon: Lightbulb,    color: '#3b82f6', cssVar: 'var(--ceo)' },
  Developer:  { label: 'Dev Lead',   Icon: Code2,        color: '#8b5cf6', cssVar: 'var(--developer)' },
  Finance:    { label: 'CFO',        Icon: DollarSign,   color: '#10b981', cssVar: 'var(--finance)' },
  Marketing:  { label: 'CMO',        Icon: Megaphone,    color: '#f59e0b', cssVar: 'var(--marketing)' },
  Risk:       { label: 'CRO',        Icon: ShieldAlert,  color: '#ef4444', cssVar: 'var(--risk)' },
  Synthesis:  { label: 'Strategist', Icon: Sparkles,     color: '#06b6d4', cssVar: 'var(--synthesis)' },
};

// Pentagon positions for agent nodes (as % from center, within a 520px arena)
const NODE_POSITIONS = {
  CEO:       { top: '14%', left: '50%',  transform: 'translate(-50%, 0)' },
  Developer: { top: '32%', left: '82%',  transform: 'translate(-50%, 0)' },
  Finance:   { top: '68%', left: '72%',  transform: 'translate(-50%, 0)' },
  Marketing: { top: '68%', left: '28%',  transform: 'translate(-50%, 0)' },
  Risk:      { top: '32%', left: '18%',  transform: 'translate(-50%, 0)' },
};

const PLAN_SECTIONS = [
  'Executive Summary', 'Technology Stack',
  'Financial Model', 'Marketing Strategy', 'Risk Assessment'
];

const PLAN_TAB_COLORS = {
  'Executive Summary':  '#3b82f6',
  'Technology Stack':   '#8b5cf6',
  'Financial Model':    '#10b981',
  'Marketing Strategy': '#f59e0b',
  'Risk Assessment':    '#ef4444',
};

const PHASES = [
  { id: 1, label: 'CEO Proposal' },
  { id: 2, label: 'Parallel Critique' },
  { id: 3, label: 'Negotiation' },
  { id: 4, label: 'Synthesis' },
];

// ── Helpers ──────────────────────────────────────────────────────────────────
function scoreColor(score) {
  if (score >= 7.5) return '#10b981';
  if (score >= 5)   return '#f59e0b';
  return '#ef4444';
}

function formatText(text) {
  if (!text) return null;
  return text.split('\n').filter(p => p.trim()).map((p, i) => (
    <p key={i} dangerouslySetInnerHTML={{
      __html: p.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    }} />
  ));
}

// ── AgentNode ────────────────────────────────────────────────────────────────
function AgentNode({ id, state }) {
  const cfg = AGENTS[id];
  const { Icon } = cfg;
  const pos = NODE_POSITIONS[id];
  if (!pos) return null;

  const status = state?.status || 'idle';
  const score  = state?.score;

  const avatarClass = [
    'agent-avatar',
    status === 'thinking' ? 'thinking' : '',
    status === 'complete' ? 'complete' : '',
    (score !== undefined && score < 5) ? 'disagreeing' : '',
  ].filter(Boolean).join(' ');

  return (
    <div className="agent-node" style={{ ...pos, position: 'absolute' }}>
      <div className={avatarClass} data-agent={id}>
        <Icon size={26} color={cfg.color} />
      </div>
      <div className="agent-name-tag" style={{ color: cfg.color }}>{cfg.label}</div>
      {score !== undefined && (
        <div className="agent-score-tag" style={{ background: scoreColor(score) }}>
          {score}/10
        </div>
      )}
    </div>
  );
}

// ── ChatBubble ───────────────────────────────────────────────────────────────
function ChatBubble({ event }) {
  const agent = event.agent || 'System';
  const cfg = AGENTS[agent] || { color: '#94a3b8', label: agent };

  const typeLabels = {
    proposal: 'Proposal',
    critique: 'Critique',
    revision: 'Revision',
    re_score: 'Re-Score',
    final_plan: 'Final Plan',
    consensus_reached: 'Convergence',
    phase_change: 'Phase',
    agent_thinking: null,
  };

  const label = typeLabels[event.type];
  if (event.type === 'agent_thinking') return null;

  const content = event.content ||
    (event.type === 'consensus_reached' ? `Consensus reached at ${event.final_score}/10` : null) ||
    (event.type === 'phase_change' ? `→ ${event.label}` : null) ||
    (event.type === 'final_plan' ? 'Business plan synthesized ✓' : null);

  if (!content) return null;

  return (
    <div className="chat-bubble">
      <div className="bubble-header">
        <span style={{ color: cfg.color }}>{cfg.label || agent}</span>
        {label && <span className="bubble-type-tag">{label}</span>}
        {event.round && <span className="bubble-type-tag">Round {event.round}</span>}
      </div>
      <div className="bubble-content" style={{ borderColor: cfg.color }}>
        {content}
        {event.score !== undefined && (
          <div className="bubble-score" style={{ color: scoreColor(event.score) }}>
            Score: {event.score}/10
          </div>
        )}
      </div>
    </div>
  );
}

// ── ConsensusMeter ───────────────────────────────────────────────────────────
function ConsensusMeter({ score, converged }) {
  const pct = Math.min((score / 10) * 100, 100);
  const color = scoreColor(score);
  return (
    <div className="consensus-section">
      <div className="consensus-card">
        <div className="consensus-header">
          <span className="consensus-title">Consensus Score</span>
          <span className="consensus-value" style={{ color }}>{score.toFixed(1)}/10</span>
        </div>
        <div className="consensus-track">
          <div
            className="consensus-fill"
            style={{ width: `${pct}%`, background: `linear-gradient(90deg, ${color}99, ${color})` }}
          />
          <div className="consensus-threshold">
            <div className="threshold-label">Target 7.5</div>
          </div>
        </div>
        {converged && (
          <div className="convergence-banner">
            <CheckCircle2 size={18} />
            Consensus reached! All agents have aligned on the proposal.
          </div>
        )}
      </div>
    </div>
  );
}

// ── FinalPlan ────────────────────────────────────────────────────────────────
function FinalPlan({ plan, pdfReady }) {
  const [active, setActive] = useState('Executive Summary');

  return (
    <div className="final-plan-section">
      <div className="final-plan-header">
        <div className="final-plan-title">📋 Consensus Business Plan</div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Synthesized from all agent insights after deliberation
        </p>
      </div>
      <div className="plan-tabs">
        {PLAN_SECTIONS.map(s => (
          <button
            key={s}
            className={`plan-tab ${active === s ? 'active' : ''}`}
            style={active === s ? { background: PLAN_TAB_COLORS[s], borderColor: PLAN_TAB_COLORS[s] } : {}}
            onClick={() => setActive(s)}
          >{s}</button>
        ))}
      </div>
      <div className="plan-content-card">
        {formatText(plan[active] || '_This section is being compiled..._')}
      </div>
      {pdfReady && (
        <a className="download-btn" href="http://localhost:8000/download-report" target="_blank" rel="noreferrer">
          <Download size={18} />
          Download PDF Business Plan
        </a>
      )}
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [idea, setIdea]           = useState('');
  const [fastMode, setFastMode]   = useState(true);
  const [running, setRunning]     = useState(false);
  const [phase, setPhase]         = useState(0);
  const [agentStates, setAgentStates] = useState({});
  const [feed, setFeed]           = useState([]);
  const [consensusScore, setConsensusScore] = useState(0);
  const [converged, setConverged] = useState(false);
  const [finalPlan, setFinalPlan] = useState(null);
  const [pdfReady, setPdfReady]   = useState(false);
  const [done, setDone]           = useState(false);
  const feedRef = useRef(null);

  const reset = () => {
    setPhase(0); setAgentStates({}); setFeed([]);
    setConsensusScore(0); setConverged(false);
    setFinalPlan(null); setPdfReady(false); setDone(false);
  };

  const addFeedItem = useCallback((event) => {
    setFeed(prev => [...prev.slice(-60), event]);
    setTimeout(() => {
      feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight, behavior: 'smooth' });
    }, 50);
  }, []);

  const handleEvent = useCallback((data) => {
    addFeedItem(data);

    switch (data.type) {
      case 'phase_change':
        setPhase(data.phase);
        break;

      case 'agent_thinking':
        setAgentStates(prev => ({
          ...prev,
          [data.agent]: { ...prev[data.agent], status: 'thinking' }
        }));
        break;

      case 'proposal':
      case 'revision':
        setAgentStates(prev => ({
          ...prev,
          CEO: { status: 'complete', content: data.content }
        }));
        break;

      case 'critique':
      case 're_score':
        setAgentStates(prev => ({
          ...prev,
          [data.agent]: { status: 'complete', score: data.score, content: data.content }
        }));
        break;

      case 'consensus_update':
        setConsensusScore(data.score);
        break;

      case 'consensus_reached':
        setConverged(true);
        setConsensusScore(data.final_score);
        break;

      case 'final_plan':
        setFinalPlan(data.plan);
        setAgentStates(prev => ({
          ...prev,
          Synthesis: { status: 'complete' }
        }));
        break;

      case 'pdf_ready':
        setPdfReady(true);
        break;

      case 'system_done':
        setDone(true);
        setRunning(false);
        break;

      default: break;
    }
  }, [addFeedItem]);

  const simulate = async () => {
    if (!idea.trim() || running) return;
    reset();
    setRunning(true);

    try {
      const res = await fetch('http://localhost:8000/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea, fast: fastMode }),
      });

      const reader = res.body.getReader();
      const dec = new TextDecoder('utf-8');
      let buf = '';

      while (true) {
        const { done: d, value } = await reader.read();
        if (d) break;
        buf += dec.decode(value, { stream: true });
        const chunks = buf.split('\n\n');
        buf = chunks.pop() || '';
        for (const chunk of chunks) {
          if (chunk.startsWith('data: ')) {
            try {
              const data = JSON.parse(chunk.slice(6));
              handleEvent(data);
            } catch (e) { /* skip malformed */ }
          }
        }
      }
    } catch (err) {
      console.error('Simulation error', err);
      setRunning(false);
    }
  };

  const activeAgents = fastMode
    ? ['CEO', 'Developer', 'Finance']
    : ['CEO', 'Developer', 'Finance', 'Marketing', 'Risk'];

  const showArena  = running || done;
  const showPlan   = !!finalPlan;
  const showMeter  = consensusScore > 0;

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="logo-badge">
          <div className="logo-dot" />
          FoundrAI 2.0 — Deliberative AI
        </div>
        <h1 className="main-title">AI Round Table</h1>
        <p className="main-subtitle">
          A consensus-driven board of AI agents debates, critiques, and collaborates
          to turn your idea into a validated business plan.
        </p>
      </header>

      {/* ── Input ── */}
      <section className="input-section">
        <div className="input-card">
          <div className="input-row">
            <textarea
              className="idea-textarea"
              value={idea}
              onChange={e => setIdea(e.target.value)}
              placeholder="Describe your startup idea… (e.g. 'An AI tutor that adapts to each student's learning style in real-time')"
              disabled={running}
              rows={3}
            />
            <button className="launch-btn" onClick={simulate} disabled={!idea.trim() || running}>
              {running
                ? <><Activity size={16} className="spin" /> Running…</>
                : <><Send size={16} /> Launch</>
              }
            </button>
          </div>
          <div className="mode-toggle">
            <span className="mode-label">
              {fastMode
                ? '⚡ Fast Mode — ~6 API calls, results in ~20s'
                : '🧠 Normal Mode — up to 14 API calls, deeper analysis'}
            </span>
            <div className="toggle-group">
              <button className={`toggle-btn ${fastMode ? 'active' : ''}`} onClick={() => setFastMode(true)}>⚡ Fast</button>
              <button className={`toggle-btn ${!fastMode ? 'active' : ''}`} onClick={() => setFastMode(false)}>🧠 Deep</button>
            </div>
          </div>
        </div>
      </section>

      {/* ── Phase Bar ── */}
      {showArena && (
        <div className="phase-bar">
          {PHASES.map((p, i) => (
            <React.Fragment key={p.id}>
              {i > 0 && <div className={`phase-connector ${phase >= p.id ? 'active' : ''}`} />}
              <div className={`phase-step ${phase === p.id ? 'active' : ''} ${phase > p.id ? 'done' : ''}`}>
                <div className="phase-dot" />
                {p.label}
              </div>
            </React.Fragment>
          ))}
        </div>
      )}

      {/* ── Round Table Arena + Chat Feed ── */}
      {showArena && (
        <div className="roundtable-wrapper">
          {/* Arena */}
          <div className="roundtable-arena">
            <div className="agents-ring">
              {/* Center Hub */}
              <div className={`center-hub ${running ? 'active' : ''}`}>
                <div className="hub-score">{consensusScore > 0 ? `${consensusScore}` : '—'}</div>
                <div className="hub-label">Consensus</div>
              </div>

              {/* Agent Nodes */}
              {activeAgents.map(id => (
                <AgentNode key={id} id={id} state={agentStates[id]} />
              ))}
              {done && finalPlan && (
                <div
                  className="agent-node"
                  style={{ bottom: '6%', left: '50%', transform: 'translate(-50%, 0)', position: 'absolute' }}
                >
                  <div className="agent-avatar complete" data-agent="Synthesis">
                    <Sparkles size={26} color="#06b6d4" />
                  </div>
                  <div className="agent-name-tag" style={{ color: '#06b6d4' }}>Strategist</div>
                </div>
              )}
            </div>
          </div>

          {/* Chat Feed */}
          <div className="chat-feed-panel">
            <div className="chat-feed-header">
              <div className="live-dot" />
              Live Discussion
              <MessageSquare size={13} style={{ marginLeft: 'auto', opacity: 0.5 }} />
            </div>
            <div className="chat-feed-body" ref={feedRef}>
              {feed.map((evt, i) => <ChatBubble key={i} event={evt} />)}
              {running && (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem', display: 'flex', gap: '6px', alignItems: 'center' }}>
                  <Activity size={12} className="spin" /> Agents deliberating…
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Consensus Meter ── */}
      {showMeter && <ConsensusMeter score={consensusScore} converged={converged} />}

      {/* ── Final Plan ── */}
      {showPlan && <FinalPlan plan={finalPlan} pdfReady={pdfReady} />}

      {/* ── Reset ── */}
      {done && (
        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <button
            onClick={() => { reset(); setIdea(''); }}
            style={{
              background: 'transparent', border: '1px solid var(--border)',
              color: 'var(--text-secondary)', padding: '10px 24px',
              borderRadius: '10px', cursor: 'pointer', fontSize: '0.88rem',
              display: 'inline-flex', alignItems: 'center', gap: '8px',
              fontFamily: 'inherit', transition: 'all 0.2s',
            }}
          >
            <RotateCcw size={14} /> New Simulation
          </button>
        </div>
      )}
    </div>
  );
}
