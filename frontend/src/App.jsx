import React, { useState, useRef, useCallback } from 'react';
import {
  Lightbulb, Code2, DollarSign, Megaphone, ShieldAlert,
  Sparkles, Send, RotateCcw, CheckCircle2, Download,
  Activity, MessageSquare, Search, Globe, Github,
  Zap, Shield, RefreshCw, ExternalLink, AlertTriangle
} from 'lucide-react';
import './index.css';

// ── Agent config ──────────────────────────────────────────────────────────────
const AGENTS = {
  CEO:       { label: 'CEO',        Icon: Lightbulb,   color: '#3b82f6' },
  Developer: { label: 'Dev Lead',   Icon: Code2,       color: '#8b5cf6' },
  Finance:   { label: 'CFO',        Icon: DollarSign,  color: '#10b981' },
  Marketing: { label: 'CMO',        Icon: Megaphone,   color: '#f59e0b' },
  Risk:      { label: 'CRO',        Icon: ShieldAlert, color: '#ef4444' },
  Synthesis: { label: 'Strategist', Icon: Sparkles,    color: '#06b6d4' },
};

const NODE_POSITIONS = {
  CEO:       { top: '14%', left: '50%',  transform: 'translate(-50%, 0)' },
  Developer: { top: '32%', left: '82%',  transform: 'translate(-50%, 0)' },
  Finance:   { top: '68%', left: '72%',  transform: 'translate(-50%, 0)' },
  Marketing: { top: '68%', left: '28%',  transform: 'translate(-50%, 0)' },
  Risk:      { top: '32%', left: '18%',  transform: 'translate(-50%, 0)' },
};

const PLAN_SECTIONS  = ['Executive Summary','Technology Stack','Financial Model','Marketing Strategy','Risk Assessment'];
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

// ── Helpers ───────────────────────────────────────────────────────────────────
function scoreColor(s) {
  if (s >= 7.5) return '#10b981';
  if (s >= 5)   return '#f59e0b';
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

// ── AgentNode ─────────────────────────────────────────────────────────────────
function AgentNode({ id, state }) {
  const cfg = AGENTS[id];
  if (!cfg) return null;
  const { Icon } = cfg;
  const pos    = NODE_POSITIONS[id];
  const status = state?.status || 'idle';
  const score  = state?.score;
  const avatarClass = ['agent-avatar',
    status === 'thinking' ? 'thinking' : '',
    status === 'complete' ? 'complete' : '',
    (score !== undefined && score < 5) ? 'disagreeing' : '',
  ].filter(Boolean).join(' ');
  if (!pos) return null;
  return (
    <div className="agent-node" style={{ ...pos, position: 'absolute' }}>
      <div className={avatarClass} data-agent={id}>
        <Icon size={26} color={cfg.color} />
      </div>
      <div className="agent-name-tag" style={{ color: cfg.color }}>{cfg.label}</div>
      {score !== undefined && (
        <div className="agent-score-tag" style={{ background: scoreColor(score) }}>{score}/10</div>
      )}
    </div>
  );
}

// ── Chat Bubbles ──────────────────────────────────────────────────────────────
function ToolCallBubble({ event }) {
  return (
    <div className="tool-call-bubble">
      <div className="tool-call-header">
        <Search size={10} />
        <span>{event.agent}</span>
        <span className="tool-call-tag">Live API</span>
        {event.rag_used && <span className="tool-call-tag" style={{ background: 'rgba(99,102,241,0.2)', color: '#a5b4fc' }}>+ RAG</span>}
      </div>
      <div className="tool-call-content">
        🔍 Querying <strong>{event.tool}</strong>: "{event.query}"
      </div>
    </div>
  );
}
function ToolResultBubble({ event }) {
  const snippet = event.snippet || '';
  if (!snippet || snippet.startsWith('[FALLBACK]')) return null;
  return (
    <div className="tool-result-bubble">
      <div className="tool-result-header">
        <Globe size={10} />
        <span className="tool-result-tag">📡 {event.tool} returned</span>
      </div>
      <div className="tool-result-content">{snippet}</div>
    </div>
  );
}
function MonitorBubble({ event }) {
  const icons = { monitor_scanning: '🔍', monitor_data: '📡', monitor_updating: '⚡', monitor_done: '✅' };
  const msg = event.message || (event.type === 'monitor_done' ? '⚡ Strategy auto-updated!' : '');
  if (!msg) return null;
  return (
    <div className="tool-call-bubble" style={{ opacity: 0.9 }}>
      <div className="tool-call-header">
        <RefreshCw size={10} className="spin" />
        <span style={{ color: '#06b6d4' }}>Auto-Monitor</span>
        <span className="tool-call-tag" style={{ background: 'rgba(6,182,212,0.15)', color: '#06b6d4' }}>Daemon</span>
      </div>
      <div className="tool-call-content" style={{ color: '#67e8f9', borderColor: 'rgba(6,182,212,0.3)' }}>
        {icons[event.type] || '⚙️'} {msg}
        {event.snippet && <div style={{ marginTop: 4, opacity: 0.7 }}>{event.snippet}</div>}
      </div>
    </div>
  );
}
function ChatBubble({ event }) {
  if (event.type === 'tool_call')       return <ToolCallBubble event={event} />;
  if (event.type === 'tool_result')     return <ToolResultBubble event={event} />;
  if (event.type?.startsWith('monitor')) return <MonitorBubble event={event} />;

  const agent = event.agent || 'System';
  const cfg   = AGENTS[agent] || { color: '#94a3b8', label: agent };
  const typeLabels = {
    proposal: 'Proposal', critique: 'Critique', revision: 'Revision',
    re_score: 'Re-Score', final_plan: 'Final Plan',
    consensus_reached: 'Convergence', phase_change: 'Phase', agent_thinking: null,
  };
  const label = typeLabels[event.type];
  if (event.type === 'agent_thinking') return null;
  const content = event.content
    || (event.type === 'consensus_reached' ? `Consensus reached at ${event.final_score}/10` : null)
    || (event.type === 'phase_change' ? `→ ${event.label}` : null)
    || (event.type === 'final_plan' ? 'Business plan synthesized ✓' : null);
  if (!content) return null;
  return (
    <div className="chat-bubble">
      <div className="bubble-header">
        <span style={{ color: cfg.color }}>{cfg.label || agent}</span>
        {label && <span className="bubble-type-tag">{label}</span>}
        {event.grounded_by && (
          <span className="tool-call-tag" style={{ background: 'rgba(99,102,241,0.1)', color: '#a5b4fc' }}>
            via {event.grounded_by}
          </span>
        )}
        {event.rag_used && (
          <span className="tool-call-tag" style={{ background: 'rgba(16,185,129,0.1)', color: '#34d399' }}>
            + RAG
          </span>
        )}
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

// ── ConsensusMeter ────────────────────────────────────────────────────────────
function ConsensusMeter({ score, converged }) {
  const pct   = Math.min((score / 10) * 100, 100);
  const color = scoreColor(score);
  return (
    <div className="consensus-section">
      <div className="consensus-card">
        <div className="consensus-header">
          <span className="consensus-title">Consensus Score</span>
          <span className="consensus-value" style={{ color }}>{score.toFixed(1)}/10</span>
        </div>
        <div className="consensus-track">
          <div className="consensus-fill" style={{ width: `${pct}%`, background: `linear-gradient(90deg, ${color}99, ${color})` }} />
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

// ── Approval Gate Modal ───────────────────────────────────────────────────────
function ApprovalModal({ idea, consensusScore, onApprove, onClose, deploying }) {
  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-icon"><Shield size={32} color="#6366f1" /></div>
        <h2 className="modal-title">Human Approval Required</h2>
        <p className="modal-subtitle">
          The AI board has reached consensus. Before autonomous deployment, your approval is required.
        </p>
        <div className="modal-score-row">
          <div className="modal-score-pill" style={{ background: `${scoreColor(consensusScore)}22`, borderColor: scoreColor(consensusScore) }}>
            <span style={{ color: scoreColor(consensusScore), fontWeight: 800, fontSize: '1.4rem' }}>
              {consensusScore.toFixed(1)}/10
            </span>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Consensus Score</span>
          </div>
        </div>
        <div className="modal-details">
          <div className="modal-detail-row"><CheckCircle2 size={14} color="#10b981" /> Business plan validated by 5 AI agents</div>
          <div className="modal-detail-row"><Github size={14} color="#a5b4fc" /> Private GitHub repo will be created: <code>{idea.split(' ').slice(0,3).join('-').toLowerCase()}-foundrai</code></div>
          <div className="modal-detail-row"><Code2 size={14} color="#8b5cf6" /> Files: README.md, docker-compose.yml, .env.example, app/main.py, foundrai.json</div>
          <div className="modal-detail-row"><AlertTriangle size={14} color="#f59e0b" /> This action is irreversible — a real GitHub repo will be created</div>
        </div>
        <div className="modal-actions">
          <button className="modal-cancel-btn" onClick={onClose} disabled={deploying}>Cancel</button>
          <button className="modal-approve-btn" onClick={onApprove} disabled={deploying}>
            {deploying ? <><Activity size={14} className="spin" /> Deploying…</> : <><Github size={14} /> Approve & Deploy</>}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Deploy Banner ─────────────────────────────────────────────────────────────
function DeployBanner({ result, files }) {
  return (
    <div className="deploy-banner">
      <div className="deploy-banner-header">
        <Github size={20} color="#10b981" />
        <span>Codebase Deployed Successfully</span>
        <CheckCircle2 size={18} color="#10b981" />
      </div>
      <a className="deploy-repo-link" href={result.repo_url} target="_blank" rel="noreferrer">
        <ExternalLink size={14} /> {result.repo_url}
      </a>
      <div className="deploy-files">
        {(result.files_generated || files || []).map(f => (
          <span key={f} className="deploy-file-chip">{f}</span>
        ))}
      </div>
    </div>
  );
}

// ── Monitor Panel ─────────────────────────────────────────────────────────────
function MonitorPanel({ idea, plan, onUpdate }) {
  const [state, setState] = useState('idle'); // idle | running | done
  const [log,   setLog]   = useState([]);

  const runMonitor = async () => {
    setState('running');
    setLog([]);
    try {
      const res = await fetch('http://localhost:8000/monitor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea }),
      });
      const reader = res.body.getReader();
      const dec = new TextDecoder('utf-8');
      let buf = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const chunks = buf.split('\n\n');
        buf = chunks.pop() || '';
        for (const chunk of chunks) {
          if (chunk.startsWith('data: ')) {
            try {
              const data = JSON.parse(chunk.slice(6));
              setLog(prev => [...prev, data]);
              if (data.type === 'monitor_done') {
                onUpdate(data.updated_section, data.updated_content);
                setState('done');
              }
            } catch {}
          }
        }
      }
    } catch (e) {
      setState('idle');
    }
  };

  return (
    <div className="monitor-panel">
      <div className="monitor-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Zap size={18} color="#06b6d4" />
          <div>
            <div className="monitor-title">Auto-Monitor Daemon</div>
            <div className="monitor-subtitle">Polls live market data and auto-updates strategy</div>
          </div>
        </div>
        <button
          className="fast-forward-btn"
          onClick={runMonitor}
          disabled={state === 'running'}
        >
          {state === 'running'
            ? <><RefreshCw size={14} className="spin" /> Scanning…</>
            : state === 'done'
            ? <><RefreshCw size={14} /> Scan Again</>
            : <><Zap size={14} /> ⏩ Fast Forward</>
          }
        </button>
      </div>
      {log.length > 0 && (
        <div className="monitor-log">
          {log.map((evt, i) => <MonitorBubble key={i} event={evt} />)}
        </div>
      )}
      {state === 'done' && (
        <div className="monitor-done-banner">
          <CheckCircle2 size={14} /> Strategy section auto-updated based on new market data
        </div>
      )}
    </div>
  );
}

// ── FinalPlan ─────────────────────────────────────────────────────────────────
function FinalPlan({ idea, plan, pdfReady, consensusScore, onDeploy, deployResult }) {
  const [active,    setActive]    = useState('Executive Summary');
  const [showModal, setShowModal] = useState(false);
  const [deploying, setDeploying] = useState(false);
  const [localPlan, setLocalPlan] = useState(plan);

  const handleApprove = async () => {
    setDeploying(true);
    try {
      const res  = await fetch('http://localhost:8000/approve-deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea, plan: localPlan }),
      });
      const data = await res.json();
      onDeploy(data);
      setShowModal(false);
    } catch (e) {
      console.error('Deploy error', e);
    } finally {
      setDeploying(false);
    }
  };

  const handleMonitorUpdate = (section, content) => {
    setLocalPlan(prev => ({ ...prev, [section]: content }));
    setActive(section);
  };

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

      <div className={`plan-content-card ${active === 'Marketing Strategy' && localPlan[active] !== plan[active] ? 'plan-updated' : ''}`}>
        {active === 'Marketing Strategy' && localPlan[active] !== plan[active] && (
          <div className="plan-updated-banner"><Zap size={12} /> Auto-updated by monitor daemon</div>
        )}
        {formatText(localPlan[active] || '_Section being compiled…_')}
      </div>

      {/* Action Row */}
      <div className="plan-action-row">
        {pdfReady && (
          <a className="download-btn" href="http://localhost:8000/download-report" target="_blank" rel="noreferrer">
            <Download size={16} /> Download PDF
          </a>
        )}
        {!deployResult && (
          <button className="deploy-btn" onClick={() => setShowModal(true)}>
            <Github size={16} /> Approve & Deploy to GitHub
          </button>
        )}
      </div>

      {/* Deploy result banner */}
      {deployResult && <DeployBanner result={deployResult} />}

      {/* Monitor panel */}
      <MonitorPanel idea={idea} plan={localPlan} onUpdate={handleMonitorUpdate} />

      {/* Approval Modal */}
      {showModal && (
        <ApprovalModal
          idea={idea}
          consensusScore={consensusScore}
          onApprove={handleApprove}
          onClose={() => setShowModal(false)}
          deploying={deploying}
        />
      )}
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [idea,          setIdea]          = useState('');
  const [fastMode,      setFastMode]      = useState(true);
  const [running,       setRunning]       = useState(false);
  const [phase,         setPhase]         = useState(0);
  const [agentStates,   setAgentStates]   = useState({});
  const [feed,          setFeed]          = useState([]);
  const [consensusScore,setConsensusScore]= useState(0);
  const [converged,     setConverged]     = useState(false);
  const [finalPlan,     setFinalPlan]     = useState(null);
  const [pdfReady,      setPdfReady]      = useState(false);
  const [done,          setDone]          = useState(false);
  const [deployResult,  setDeployResult]  = useState(null);
  const feedRef = useRef(null);

  const reset = () => {
    setPhase(0); setAgentStates({}); setFeed([]);
    setConsensusScore(0); setConverged(false);
    setFinalPlan(null); setPdfReady(false);
    setDone(false); setDeployResult(null);
  };

  const addFeedItem = useCallback((event) => {
    setFeed(prev => [...prev.slice(-80), event]);
    setTimeout(() => {
      feedRef.current?.scrollTo({ top: feedRef.current.scrollHeight, behavior: 'smooth' });
    }, 50);
  }, []);

  const handleEvent = useCallback((data) => {
    addFeedItem(data);
    switch (data.type) {
      case 'phase_change':
        setPhase(data.phase); break;
      case 'agent_thinking':
        setAgentStates(prev => ({ ...prev, [data.agent]: { ...prev[data.agent], status: 'thinking' } })); break;
      case 'proposal':
      case 'revision':
        setAgentStates(prev => ({ ...prev, CEO: { status: 'complete', content: data.content } })); break;
      case 'critique':
      case 're_score':
        setAgentStates(prev => ({ ...prev, [data.agent]: { status: 'complete', score: data.score } })); break;
      case 'consensus_update':
        setConsensusScore(data.score); break;
      case 'consensus_reached':
        setConverged(true); setConsensusScore(data.final_score); break;
      case 'final_plan':
        setFinalPlan(data.plan);
        setAgentStates(prev => ({ ...prev, Synthesis: { status: 'complete' } })); break;
      case 'pdf_ready':
        setPdfReady(true); break;
      case 'system_done':
        setDone(true); setRunning(false); break;
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
            try { handleEvent(JSON.parse(chunk.slice(6))); } catch {}
          }
        }
      }
    } catch (err) {
      console.error(err);
      setRunning(false);
    }
  };

  const activeAgents = fastMode
    ? ['CEO', 'Developer', 'Finance']
    : ['CEO', 'Developer', 'Finance', 'Marketing', 'Risk'];

  const showArena = running || done;
  const showMeter = consensusScore > 0;
  const showPlan  = !!finalPlan;

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="logo-badge">
          <div className="logo-dot" />
          FoundrAI 2.0 — Deliberative AI
        </div>
        <h1 className="main-title">AI Round Table</h1>
        <p className="main-subtitle">
          Agents debate with live data, reach consensus via RAG + tool use, then autonomously deploy your codebase to GitHub.
        </p>
      </header>

      {/* Input */}
      <section className="input-section">
        <div className="input-card">
          <div className="input-row">
            <textarea className="idea-textarea" value={idea}
              onChange={e => setIdea(e.target.value)}
              placeholder="Describe your startup idea… (e.g. 'An AI tutor that adapts to each student's learning style in real-time')"
              disabled={running} rows={3}
            />
            <button className="launch-btn" onClick={simulate} disabled={!idea.trim() || running}>
              {running ? <><Activity size={16} className="spin" /> Running…</> : <><Send size={16} /> Launch</>}
            </button>
          </div>
          <div className="mode-toggle">
            <span className="mode-label">
              {fastMode ? '⚡ Fast Mode — ~8 API calls + RAG' : '🧠 Deep Mode — ~16 calls, all 5 agents + RAG'}
            </span>
            <div className="toggle-group">
              <button className={`toggle-btn ${fastMode ? 'active' : ''}`} onClick={() => setFastMode(true)}>⚡ Fast</button>
              <button className={`toggle-btn ${!fastMode ? 'active' : ''}`} onClick={() => setFastMode(false)}>🧠 Deep</button>
            </div>
          </div>
        </div>
      </section>

      {/* Phase Bar */}
      {showArena && (
        <div className="phase-bar">
          {PHASES.map((p, i) => (
            <React.Fragment key={p.id}>
              {i > 0 && <div className={`phase-connector ${phase >= p.id ? 'active' : ''}`} />}
              <div className={`phase-step ${phase === p.id ? 'active' : ''} ${phase > p.id ? 'done' : ''}`}>
                <div className="phase-dot" />{p.label}
              </div>
            </React.Fragment>
          ))}
        </div>
      )}

      {/* Round Table + Feed */}
      {showArena && (
        <div className="roundtable-wrapper">
          <div className="roundtable-arena">
            <div className="agents-ring">
              <div className={`center-hub ${running ? 'active' : ''}`}>
                <div className="hub-score">{consensusScore > 0 ? `${consensusScore}` : '—'}</div>
                <div className="hub-label">Consensus</div>
              </div>
              {activeAgents.map(id => (
                <AgentNode key={id} id={id} state={agentStates[id]} />
              ))}
              {done && finalPlan && (
                <div className="agent-node" style={{ bottom: '6%', left: '50%', transform: 'translate(-50%,0)', position: 'absolute' }}>
                  <div className="agent-avatar complete" data-agent="Synthesis">
                    <Sparkles size={26} color="#06b6d4" />
                  </div>
                  <div className="agent-name-tag" style={{ color: '#06b6d4' }}>Strategist</div>
                </div>
              )}
            </div>
          </div>
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

      {/* Consensus Meter */}
      {showMeter && <ConsensusMeter score={consensusScore} converged={converged} />}

      {/* Final Plan + Deploy + Monitor */}
      {showPlan && (
        <FinalPlan
          idea={idea}
          plan={finalPlan}
          pdfReady={pdfReady}
          consensusScore={consensusScore}
          onDeploy={setDeployResult}
          deployResult={deployResult}
        />
      )}

      {/* Reset */}
      {done && (
        <div style={{ textAlign: 'center', marginTop: '24px' }}>
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
