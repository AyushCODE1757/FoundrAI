"use client";
import { useState, useRef, useCallback } from "react";
import { ArrowRight, CheckCircle2 } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import PhaseBar from "./PhaseBar";
import RoundTable from "./RoundTable";
import LiveFeed from "./LiveFeed";
import LivingDocument from "./LivingDocument";

export default function ActiveStage() {
  const { planReady, consensusScore, goToResults } = useAppStore();

  const [leftPct, setLeftPct] = useState(65);
  const containerRef = useRef(null);
  const dragging = useRef(false);

  const onMouseDown = useCallback((e) => {
    e.preventDefault();
    dragging.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  const onMouseMove = useCallback((e) => {
    if (!dragging.current || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const raw = ((e.clientX - rect.left) / rect.width) * 100;
    setLeftPct(Math.min(80, Math.max(40, raw)));
  }, []);

  const onMouseUp = useCallback(() => {
    dragging.current = false;
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
  }, []);

  return (
    <>
      <PhaseBar />

      <div
        ref={containerRef}
        className="flex p-4 gap-0"
        style={{
          height: planReady ? "calc(100vh - 11rem)" : "calc(100vh - 7.5rem)",
        }}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
      >
        <div
          className="glass rounded-2xl overflow-hidden flex items-center justify-center flex-shrink-0"
          style={{ width: `calc(${leftPct}% - 6px)` }}
        >
          <RoundTable />
        </div>

        <div
          className="flex-shrink-0 flex items-center justify-center cursor-col-resize group"
          style={{ width: 12, zIndex: 10 }}
          onMouseDown={onMouseDown}
        >
          <div className="w-0.5 h-16 rounded-full bg-white/10 group-hover:bg-indigo-500/60 transition-colors duration-150" />
        </div>

        <div
          className="flex flex-col gap-4 flex-shrink-0 min-w-0"
          style={{ width: `calc(${100 - leftPct}% - 6px)` }}
        >
          <div className="flex-1 glass rounded-2xl overflow-hidden min-h-0">
            <LiveFeed />
          </div>
          <div className="flex-1 glass rounded-2xl overflow-hidden min-h-0">
            <LivingDocument />
          </div>
        </div>
      </div>

      {/* CTA banner — only shows when plan is ready, user must click */}
      {planReady && (
        <div className="mx-4 mb-4 animate-fade-in-up">
          <div className="rounded-2xl border border-emerald-500/40 bg-gradient-to-r from-emerald-500/10 to-indigo-500/10 px-6 py-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <CheckCircle2
                size={22}
                className="text-emerald-400 flex-shrink-0"
              />
              <div>
                <div className="text-white font-bold text-sm">
                  Business Plan Ready — Consensus: {consensusScore.toFixed(1)}
                  /10
                </div>
                <div className="text-slate-400 text-xs mt-0.5">
                  All agents completed analysis. Click to view the full results.
                </div>
              </div>
            </div>
            <button
              onClick={goToResults}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm transition-all shadow-lg shadow-indigo-500/25 whitespace-nowrap flex-shrink-0"
            >
              View Full Results <ArrowRight size={15} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
