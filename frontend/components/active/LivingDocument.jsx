"use client";
import { useAppStore } from "@/store/useAppStore";
import { PLAN_SECTIONS, AGENTS } from "@/lib/utils";

function SectionSkeleton({ label }) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
      <div className="text-[10px] font-semibold text-slate-600 mb-3 font-fira">
        {label}
      </div>
      <div className="space-y-2">
        <div className="h-2.5 rounded skeleton-shimmer w-full" />
        <div className="h-2.5 rounded skeleton-shimmer w-4/5" />
        <div className="h-2.5 rounded skeleton-shimmer w-3/5" />
      </div>
    </div>
  );
}

function SectionFilled({ label, content, agentId }) {
  const cfg = AGENTS[agentId];
  const paras = content
    .split("\n")
    .filter((p) => p.trim())
    .slice(0, 3);

  return (
    <div
      className="rounded-xl border p-4 animate-fade-in"
      style={{
        borderColor: `${cfg?.color}30`,
        background: `${cfg?.color}08`,
      }}
    >
      <div className="flex items-center gap-2 mb-3">
        <span className="text-sm">{cfg?.emoji}</span>
        <span
          className="text-[10px] font-bold tracking-widest font-fira"
          style={{ color: cfg?.color }}
        >
          {label}
        </span>
        <span className="ml-auto text-[9px] text-slate-600 font-fira">
          FILLED
        </span>
      </div>
      <div className="space-y-1.5">
        {paras.map((p, i) => (
          <p
            key={i}
            className="text-[11px] text-slate-300 leading-relaxed font-fira"
            dangerouslySetInnerHTML={{
              __html: p.replace(
                /\*\*(.*?)\*\*/g,
                '<strong class="text-white">$1</strong>',
              ),
            }}
          />
        ))}
      </div>
    </div>
  );
}

export default function LivingDocument() {
  const { livingDoc } = useAppStore();

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06] flex-shrink-0">
        <span className="text-[11px] font-semibold text-slate-400 tracking-widest">
          LIVING DOCUMENT
        </span>
        <span className="ml-auto text-[10px] font-fira text-slate-600">
          fills in real-time
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-0">
        {PLAN_SECTIONS.map(({ key, label, agent }) => {
          const content = livingDoc[key];
          return content ? (
            <SectionFilled
              key={key}
              label={label}
              content={content}
              agentId={agent}
            />
          ) : (
            <SectionSkeleton key={key} label={label} />
          );
        })}
      </div>
    </div>
  );
}
