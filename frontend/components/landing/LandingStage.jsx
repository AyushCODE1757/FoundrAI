"use client";
import { useState } from "react";
import { Send, Zap, Brain, Eye, Cpu, Rocket } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { useSimulation } from "@/hooks/useSimulation";
import { TICKER_MESSAGES } from "@/lib/utils";

export default function LandingStage() {
  const { idea, setIdea, fastMode } = useAppStore();
  const { run } = useSimulation();
  const [loading, setLoading] = useState(false);

  const handleLaunch = async () => {
    if (!idea.trim() || loading) return;
    setLoading(true);
    await run();
    setLoading(false);
  };

  const doubled = [...TICKER_MESSAGES, ...TICKER_MESSAGES];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 pb-24 pt-20">
      {/* Hero */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-xs font-semibold mb-6 tracking-wide">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse-dot" />
          MULTI-AGENT AI CONSENSUS ENGINE
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold text-white tracking-tight leading-[1.05] mb-5">
          Autonomous Business
          <br />
          <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
            Validation Engine.
          </span>
        </h1>
        <p className="text-slate-400 text-lg leading-relaxed max-w-xl mx-auto">
          Stop guessing. Let agents fetch real market data, debate the strategy,
          and deploy the code.
        </p>
      </div>

      {/* Input block */}
      <div className="w-full max-w-2xl">
        <div
          className="glass rounded-2xl overflow-hidden mb-4 transition-all"
          style={{ border: "1px solid rgba(255,255,255,0.08)" }}
        >
          <textarea
            className="w-full bg-transparent px-6 py-5 text-white placeholder-slate-600 resize-none outline-none text-base leading-relaxed font-sans"
            rows={4}
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder="Describe your startup idea in plain English..."
            onKeyDown={(e) => {
              if (e.key === "Enter" && e.metaKey) handleLaunch();
            }}
          />
          <div className="px-6 py-3 border-t border-white/[0.06] flex items-center justify-between">
            <span className="text-xs text-slate-600 font-fira">
              INPUT TERMINAL V2.04
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse-dot" />
          </div>
        </div>

        {/* Mode + Launch */}
        <div className="flex gap-3">
          <button
            onClick={() => useAppStore.getState().setFastMode(true)}
            className={`flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl border font-semibold text-sm transition-all ${
              fastMode
                ? "bg-white/[0.06] border-white/20 text-white"
                : "border-white/[0.06] text-slate-500 hover:text-slate-300"
            }`}
          >
            <Zap size={15} className={fastMode ? "text-indigo-400" : ""} />
            Fast Mode
            <span className="text-xs font-normal text-slate-500">~30s</span>
          </button>

          <button
            onClick={() => useAppStore.getState().setFastMode(false)}
            className={`flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl border font-semibold text-sm transition-all ${
              !fastMode
                ? "bg-white/[0.06] border-white/20 text-white"
                : "border-white/[0.06] text-slate-500 hover:text-slate-300"
            }`}
          >
            <Brain size={15} className={!fastMode ? "text-violet-400" : ""} />
            Deep Mode
            <span className="text-xs font-normal text-slate-500">5 agents</span>
          </button>

          <button
            onClick={handleLaunch}
            disabled={!idea.trim() || loading}
            className="flex-1 flex items-center justify-center gap-2 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold text-sm transition-all shadow-lg shadow-indigo-500/20"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Launching…
              </>
            ) : (
              <>
                <Send size={15} /> Launch
              </>
            )}
          </button>
        </div>
      </div>

      {/* Perceive → Reason → Act */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl w-full mt-16">
        {[
          {
            Icon: Eye,
            title: "Perceive",
            desc: "Agents scan live web, Reddit and market reports for real demand signals.",
            tag: "DATA LAYER",
            color: "text-blue-400",
          },
          {
            Icon: Cpu,
            title: "Reason",
            desc: "Multi-agent consensus protocol debates strategy and finds fatal flaws.",
            tag: "CONSENSUS",
            color: "text-indigo-400",
          },
          {
            Icon: Rocket,
            title: "Act",
            desc: "Generates pitch deck PDF, starter code and GitHub repo in minutes.",
            tag: "DEPLOYMENT",
            color: "text-violet-400",
          },
        ].map(({ Icon, title, desc, tag, color }) => (
          <div key={title} className="glass rounded-xl p-5">
            <Icon size={20} className={`${color} mb-3`} />
            <div className="text-white font-bold text-base mb-2">{title}</div>
            <p className="text-slate-500 text-xs leading-relaxed font-fira mb-4">
              {desc}
            </p>
            <div className="flex items-center gap-2">
              <div className="h-px flex-1 bg-white/10" />
              <span className="text-slate-600 text-[10px] font-semibold tracking-widest">
                {tag}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Ticker bar */}
      <div className="fixed bottom-0 left-0 right-0 h-9 bg-[#0a0a0f]/95 border-t border-white/[0.06] overflow-hidden flex items-center">
        <div className="ticker-track flex items-center whitespace-nowrap">
          {doubled.map((msg, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-2 px-8 text-[11px] font-fira text-slate-600 border-r border-white/[0.04]"
            >
              <span className="w-1 h-1 rounded-full bg-indigo-500 flex-shrink-0" />
              {msg}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
