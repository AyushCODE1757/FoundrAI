// "use client";
// import { useRef, useEffect } from "react";
// import { useAppStore } from "@/store/useAppStore";
// import { AGENTS } from "@/lib/utils";

// function FeedCard({ event }) {
//   const { type, agent, content, score, round } = event;

//   if (
//     type === "agent_thinking" ||
//     type === "ping" ||
//     type === "consensus_update"
//   ) {
//     return null;
//   }

//   const cfg = agent ? AGENTS[agent] : null;

//   if (type === "phase_change") {
//     return (
//       <div className="flex items-center gap-2 py-1">
//         <div className="h-px flex-1 bg-white/[0.06]" />
//         <span className="text-[10px] font-fira text-slate-600 tracking-widest px-2">
//           PHASE {event.phase}
//         </span>
//         <div className="h-px flex-1 bg-white/[0.06]" />
//       </div>
//     );
//   }

//   if (type === "consensus_reached") {
//     return (
//       <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 animate-fade-in-up">
//         <span className="text-emerald-400 font-bold text-xs font-fira">
//           ✅ CONSENSUS REACHED — Score: {event.final_score}/10
//         </span>
//       </div>
//     );
//   }

//   if (type === "final_plan") {
//     return (
//       <div className="rounded-lg border border-violet-500/30 bg-violet-500/10 p-3 animate-fade-in-up">
//         <span className="text-violet-400 font-bold text-xs font-fira">
//           ✨ Business plan synthesized and ready
//         </span>
//       </div>
//     );
//   }

//   const typeMap = {
//     proposal: "PROPOSAL",
//     critique: "CRITIQUE",
//     revision: "REVISION",
//     re_score: "RE-SCORE",
//   };
//   const typeLabel = typeMap[type] || type.toUpperCase();
//   const text = content || "";

//   return (
//     <div
//       className="animate-fade-in-up pl-3 py-1.5 border-l-2"
//       style={{ borderLeftColor: cfg?.color || "#334155" }}
//     >
//       <div className="flex items-center gap-2 mb-1 flex-wrap">
//         <span
//           className="text-[10px] font-semibold"
//           style={{ color: cfg?.color || "#94a3b8" }}
//         >
//           {cfg?.emoji} {cfg?.label || agent || "SYSTEM"}
//         </span>
//         <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/[0.06] text-slate-500 font-fira tracking-wide">
//           {typeLabel}
//         </span>
//         {round && (
//           <span className="text-[9px] text-slate-600 font-fira">R{round}</span>
//         )}
//         {score !== undefined && (
//           <span
//             className="text-[10px] font-bold ml-auto"
//             style={{
//               color:
//                 score >= 7.5 ? "#10b981" : score >= 5 ? "#f59e0b" : "#ef4444",
//             }}
//           >
//             {score}/10
//           </span>
//         )}
//       </div>
//       {text && (
//         <p className="text-[11px] font-fira text-slate-400 leading-relaxed line-clamp-3">
//           {text}
//         </p>
//       )}
//     </div>
//   );
// }

// export default function LiveFeed() {
//   const { feed, stage } = useAppStore();
//   const bodyRef = useRef(null);

//   useEffect(() => {
//     if (bodyRef.current) {
//       bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
//     }
//   }, [feed.length]);

//   return (
//     <div className="flex flex-col h-full">
//       <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06] flex-shrink-0">
//         <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-dot" />
//         <span className="text-[11px] font-semibold text-slate-400 tracking-widest">
//           LIVE ACTIVITY FEED
//         </span>
//       </div>

//       <div
//         ref={bodyRef}
//         className="flex-1 overflow-y-auto p-3 space-y-2 min-h-0"
//       >
//         {feed.length === 0 ? (
//           <p className="text-slate-700 text-xs font-fira text-center mt-8">
//             Waiting for agents...
//           </p>
//         ) : (
//           feed.map((evt) => <FeedCard key={evt.id} event={evt} />)
//         )}

//         {stage === "active" && (
//           <div className="flex items-center gap-2 text-slate-600 text-[10px] font-fira py-1">
//             <span className="w-1 h-1 rounded-full bg-indigo-500 animate-pulse-dot" />
//             Agents deliberating...
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

"use client";
import { useRef, useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";
import { AGENTS } from "@/lib/utils";

// Maps event type + agent context → rich elaborated heading
function buildHeading(type, cfg, score, round, tool, source) {
  const phaseMap = {
    proposal: 1,
    critique: 2,
    re_score: 3,
    revision: 3,
    final_plan: 4,
  };

  switch (type) {
    case "proposal":
      return {
        prefix: cfg?.emoji || "🧠",
        name: cfg?.label || "CEO",
        badge: "PROPOSAL",
        sub: "Initial business plan drafted",
        color: cfg?.color,
      };
    case "critique":
      return {
        prefix: cfg?.emoji || "🔍",
        name: cfg?.label || "Agent",
        badge: "CRITIQUE",
        sub: source ? `via ${source}` : "Scoring the proposal",
        score,
        color: cfg?.color,
      };
    case "re_score":
      return {
        prefix: cfg?.emoji || "🔄",
        name: cfg?.label || "Agent",
        badge: "RE-SCORE",
        sub: `Round ${round || 1} — Updated evaluation`,
        score,
        color: cfg?.color,
      };
    case "revision":
      return {
        prefix: "✏️",
        name: "CEO",
        badge: "REVISION",
        sub: `Round ${round || 1} — Incorporating agent feedback`,
        color: AGENTS["CEO"]?.color,
      };
    case "tool_call":
      return {
        prefix: "🔎",
        name: cfg?.label || "Agent",
        badge: "LIVE API",
        sub: tool ? `Querying ${tool}` : "Calling external API",
        color: cfg?.color,
        isLive: true,
      };
    case "tool_result":
      return {
        prefix: "🌐",
        name: tool || "API",
        badge: "RETURNED",
        sub: "Live data retrieved",
        color: "#22d3ee",
      };
    default:
      return {
        prefix: cfg?.emoji || "⚙️",
        name: cfg?.label || "SYSTEM",
        badge: type.toUpperCase().replace(/_/g, " "),
        color: cfg?.color || "#64748b",
      };
  }
}

export function FeedCard({ event, compact = false }) {
  const { type, agent, content, score, round, tool, source } = event;

  if (!type) return null;
  if (["agent_thinking", "ping", "consensus_update"].includes(type))
    return null;

  const cfg = agent ? AGENTS[agent] : null;

  // ── Phase divider ──────────────────────────────────────────
  if (type === "phase_change") {
    const phaseLabels = {
      1: "CEO Proposal",
      2: "Parallel Critique",
      3: "Negotiation & Revision",
      4: "Synthesis",
    };
    return (
      <div className="flex items-center gap-2 py-2">
        <div className="h-px flex-1 bg-white/[0.07]" />
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full border border-indigo-500/20 bg-indigo-500/10">
          <span className="text-[9px] font-fira text-indigo-400 tracking-widest">
            ⚙️ SYSTEM [PHASE] →{" "}
            {phaseLabels[event.phase] || `Phase ${event.phase}`}
          </span>
        </div>
        <div className="h-px flex-1 bg-white/[0.07]" />
      </div>
    );
  }

  // ── Consensus reached ──────────────────────────────────────
  if (type === "consensus_reached") {
    return (
      <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 animate-fade-in-up">
        <div className="text-emerald-400 font-bold text-xs font-fira">
          ✅ CONSENSUS REACHED — Score: {event.final_score}/10
        </div>
        <div className="text-emerald-600 text-[10px] font-fira mt-0.5">
          Threshold 7.5 crossed. Proceeding to synthesis.
        </div>
      </div>
    );
  }

  // ── Final plan ─────────────────────────────────────────────
  if (type === "final_plan") {
    return (
      <div className="rounded-lg border border-violet-500/30 bg-violet-500/10 p-3 animate-fade-in-up">
        <div className="text-violet-400 font-bold text-xs font-fira">
          ✨ STRATEGIST [SYNTHESIS]
        </div>
        <div className="text-violet-300 text-[11px] font-fira mt-0.5">
          Business plan synthesized and ready for review.
        </div>
      </div>
    );
  }

  // ── Monitor events ─────────────────────────────────────────
  if (type === "monitor_alert" || type === "auto_revision") {
    return (
      <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-3">
        <span className="text-amber-400 font-bold text-xs font-fira">
          {content}
        </span>
      </div>
    );
  }

  // ── Standard agent event ───────────────────────────────────
  const h = buildHeading(type, cfg, score, round, tool, source);
  const text = content || "";

  return (
    <div
      className="rounded-lg border border-white/[0.05] bg-white/[0.02] overflow-hidden animate-fade-in-up"
      style={{ borderLeftColor: h.color, borderLeftWidth: 2 }}
    >
      {/* Header row */}
      <div className="flex items-center gap-2 px-3 pt-2.5 pb-1 flex-wrap">
        <span className="text-sm leading-none">{h.prefix}</span>
        <span className="text-[11px] font-bold" style={{ color: h.color }}>
          {h.name?.toUpperCase()}
        </span>
        <span
          className={`text-[9px] px-1.5 py-0.5 rounded font-fira font-semibold tracking-wide ${
            h.isLive
              ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
              : "bg-white/[0.06] text-slate-500"
          }`}
        >
          [{h.badge}]
        </span>
        {round && (
          <span className="text-[9px] text-slate-600 font-fira">
            [ROUND {round}]
          </span>
        )}
        {h.score !== undefined && (
          <span
            className="ml-auto text-[11px] font-bold font-fira"
            style={{
              color:
                h.score >= 7.5
                  ? "#10b981"
                  : h.score >= 5
                    ? "#f59e0b"
                    : "#ef4444",
            }}
          >
            {h.score}/10
          </span>
        )}
      </div>

      {/* Sub-label */}
      {h.sub && (
        <div className="px-3 pb-1">
          <span className="text-[9px] text-slate-600 font-fira italic">
            {h.sub}
          </span>
        </div>
      )}

      {/* Content */}
      {text && (
        <div className="px-3 pb-2.5">
          <p
            className={`font-fira text-slate-400 leading-relaxed ${compact ? "text-[10px] line-clamp-3" : "text-[11px] line-clamp-5"}`}
          >
            {text}
          </p>
        </div>
      )}
    </div>
  );
}

export default function LiveFeed() {
  const { feed, stage } = useAppStore();
  const bodyRef = useRef(null);

  useEffect(() => {
    if (bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [feed.length]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06] flex-shrink-0">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-dot" />
        <span className="text-[11px] font-semibold text-slate-400 tracking-widest">
          LIVE ACTIVITY FEED
        </span>
        <span className="ml-auto text-[10px] font-fira text-slate-700">
          {feed.length} events
        </span>
      </div>
      <div
        ref={bodyRef}
        className="flex-1 overflow-y-auto p-3 space-y-2 min-h-0"
      >
        {feed.length === 0 ? (
          <p className="text-slate-700 text-xs font-fira text-center mt-8">
            Waiting for agents...
          </p>
        ) : (
          feed.map((evt) => <FeedCard key={evt.id} event={evt} compact />)
        )}
        {stage === "active" && (
          <div className="flex items-center gap-2 text-slate-600 text-[10px] font-fira py-1">
            <span className="w-1 h-1 rounded-full bg-indigo-500 animate-pulse-dot" />
            Agents deliberating...
          </div>
        )}
      </div>
    </div>
  );
}
