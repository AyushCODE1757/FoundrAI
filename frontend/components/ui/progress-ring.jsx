"use client";

export function ProgressRing({ score = 0, size = 160, stroke = 8 }) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(score / 10, 1);
  const offset = circ * (1 - pct);
  const thresholdAngle = (7.5 / 10) * 360;
  const color = score >= 7.5 ? "#10b981" : score >= 5 ? "#f59e0b" : "#6366f1";

  return (
    <svg width={size} height={size} className="rotate-[-90deg]">
      {/* Track */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="rgba(255,255,255,0.06)"
        strokeWidth={stroke}
      />
      {/* Fill */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={stroke}
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="round"
        style={{
          transition:
            "stroke-dashoffset 0.6s cubic-bezier(.4,0,.2,1), stroke 0.4s ease",
        }}
      />
      {/* Threshold dot at 7.5/10 = 75% */}
      <circle
        cx={size / 2 + r * Math.cos((thresholdAngle * Math.PI) / 180)}
        cy={size / 2 + r * Math.sin((thresholdAngle * Math.PI) / 180)}
        r={4}
        fill="#64748b"
      />
    </svg>
  );
}
