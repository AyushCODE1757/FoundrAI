import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function scoreColor(score) {
  if (score >= 7.5) return "#10b981";
  if (score >= 5) return "#f59e0b";
  return "#ef4444";
}

export const AGENTS = {
  CEO: {
    label: "CEO Agent",
    role: "Strategic Vision",
    emoji: "🧠",
    color: "#6366f1",
    border: "border-indigo-500/40",
    bg: "bg-indigo-500/10",
  },
  Developer: {
    label: "Dev Agent",
    role: "Engineering",
    emoji: "⚡",
    color: "#3b82f6",
    border: "border-blue-500/40",
    bg: "bg-blue-500/10",
  },
  Finance: {
    label: "Finance Agent",
    role: "Financial Model",
    emoji: "📈",
    color: "#10b981",
    border: "border-emerald-500/40",
    bg: "bg-emerald-500/10",
  },
  Marketing: {
    label: "Marketing Agent",
    role: "Market Strategy",
    emoji: "🌐",
    color: "#f59e0b",
    border: "border-amber-500/40",
    bg: "bg-amber-500/10",
  },
  Risk: {
    label: "Risk Agent",
    role: "Risk Assessment",
    emoji: "⚠️",
    color: "#ef4444",
    border: "border-red-500/40",
    bg: "bg-red-500/10",
  },
  Synthesis: {
    label: "Strategist",
    role: "Synthesis",
    emoji: "✨",
    color: "#8b5cf6",
    border: "border-violet-500/40",
    bg: "bg-violet-500/10",
  },
};

export const PLAN_SECTIONS = [
  { key: "Executive Summary", label: "📋 Executive Summary", agent: "CEO" },
  {
    key: "Marketing Strategy",
    label: "📣 Market Analysis",
    agent: "Marketing",
  },
  { key: "Risk Assessment", label: "⚠️ Risk Assessment", agent: "Risk" },
  { key: "Financial Model", label: "💰 Finance Projections", agent: "Finance" },
  { key: "Technology Stack", label: "💻 Tech Stack", agent: "Developer" },
];

export const TICKER_MESSAGES = [
  "🌐 MARKET AGENT: Analyzing SaaS trends in APAC…",
  "🧠 CEO AGENT: Resolving conflict in monetization strategy…",
  "⚡ DEV AGENT: Spinning up cloud instances for validation…",
  "📈 FINANCE AGENT: Calculating TAM for startup idea…",
  "⚠️ RISK AGENT: Scanning EU regulatory landscape…",
  "✨ SYNTHESIS AGENT: Compiling consensus business plan…",
];
