"use client";
import { Check } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";

const PHASES = [
  { id: 1, label: "CEO Proposal" },
  { id: 2, label: "Parallel Critique" },
  { id: 3, label: "Revision" },
  { id: 4, label: "Synthesis" },
];

export default function PhaseBar() {
  const { phase, idea } = useAppStore();

  return (
    <div className="border-b border-white/[0.06] bg-[#0a0a0f]/60 backdrop-blur-sm">
      {/* Collapsed idea strip */}
      <div className="px-6 py-2 flex items-center gap-3 border-b border-white/[0.04]">
        <span className="text-[10px] text-slate-600 font-fira tracking-widest flex-shrink-0">
          IDEA
        </span>
        <p className="text-xs text-slate-400 truncate">{idea}</p>
      </div>

      {/* Phase stepper */}
      <div className="px-6 py-3 flex items-center justify-between">
        <div className="flex items-center">
          {PHASES.map((p, i) => {
            const done = phase > p.id;
            const active = phase === p.id;
            return (
              <div key={p.id} className="flex items-center">
                {i > 0 && (
                  <div
                    className={`h-px w-8 mx-1 transition-all duration-500 ${
                      done || active ? "bg-indigo-500" : "bg-white/[0.08]"
                    }`}
                  />
                )}
                <div
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition-all duration-300 ${
                    done
                      ? "text-emerald-400"
                      : active
                        ? "text-white bg-indigo-500/20 border border-indigo-500/40"
                        : "text-slate-600"
                  }`}
                >
                  {done ? (
                    <Check size={11} className="text-emerald-400" />
                  ) : (
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        active
                          ? "bg-indigo-400 animate-pulse-dot"
                          : "bg-slate-700"
                      }`}
                    />
                  )}
                  {p.label}
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-dot" />
          MONITOR: ACTIVE
        </div>
      </div>
    </div>
  );
}
