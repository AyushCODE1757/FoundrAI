"use client";
import { Zap, Brain, GitBranch } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";

export default function Navbar() {
  const { fastMode, setFastMode, stage, converged } = useAppStore();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-14 flex items-center px-6 border-b border-white/[0.06] bg-[#0a0a0f]/90 backdrop-blur-xl">
      {/* Logo */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <span className="text-white font-bold text-base tracking-tight">
          FoundrAI
        </span>
        <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
          2.0
        </span>
        {converged && (
          <span className="ml-2 text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-dot" />
            VERIFIED
          </span>
        )}
      </div>

      <div className="ml-auto flex items-center gap-3">
        {/* Mode toggle */}
        <div className="flex items-center bg-white/[0.04] border border-white/[0.08] rounded-lg p-1 gap-1">
          <button
            onClick={() => setFastMode(true)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
              fastMode
                ? "bg-indigo-500 text-white shadow-lg"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Zap size={12} /> Fast
          </button>
          <button
            onClick={() => setFastMode(false)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
              !fastMode
                ? "bg-indigo-500 text-white shadow-lg"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Brain size={12} /> Deep
          </button>
        </div>

        {/* Status dot */}
        <div className="flex items-center gap-1.5">
          <span
            className={`w-2 h-2 rounded-full ${
              stage === "active"
                ? "bg-emerald-400 animate-pulse-dot"
                : "bg-slate-600"
            }`}
          />
          <span className="text-xs text-slate-500 font-medium">
            {stage === "active" ? "LIVE" : "IDLE"}
          </span>
        </div>

        <button className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors text-xs border border-white/[0.08] rounded-lg px-3 py-1.5">
          <GitBranch size={13} /> Star
        </button>
      </div>
    </header>
  );
}
