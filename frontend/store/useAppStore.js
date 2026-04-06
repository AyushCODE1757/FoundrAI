"use client";
import { create } from "zustand";

const init = {
  stage: "landing",
  idea: "",
  fastMode: true,
  phase: 0,
  agentStates: {},
  feed: [],
  consensusScore: 0,
  converged: false,
  finalPlan: null,
  planReady: false, // NEW — true when final_plan arrives
  simulationDone: false, // NEW — true when system_done arrives
  pdfReady: false,
  deploymentUrl: "",
  livingDoc: {},
};

export const useAppStore = create((set, get) => ({
  ...init,

  setIdea: (idea) => set({ idea }),
  setFastMode: (v) => set({ fastMode: v }),

  // User explicitly clicks "View Full Results"
  goToResults: () => set({ stage: "results" }),

  reset: () => set({ ...init, idea: "" }),

  handleEvent: (data) => {
    if (data.type !== "ping") {
      set((s) => ({
        feed: [
          ...s.feed.slice(-200),
          { ...data, id: Date.now() + Math.random() },
        ],
      }));
    }

    switch (data.type) {
      case "phase_change":
        set({ phase: data.phase });
        break;

      case "agent_thinking":
        set((s) => ({
          agentStates: {
            ...s.agentStates,
            [data.agent]: { ...s.agentStates[data.agent], status: "thinking" },
          },
        }));
        break;

      case "proposal":
      case "revision":
        set((s) => ({
          agentStates: {
            ...s.agentStates,
            CEO: { status: "complete", content: data.content },
          },
          livingDoc: { ...s.livingDoc, "Executive Summary": data.content },
        }));
        break;

      case "critique":
      case "re_score": {
        const agent = data.agent;
        set((s) => ({
          agentStates: {
            ...s.agentStates,
            [agent]: {
              status: "complete",
              score: data.score,
              content: data.content,
            },
          },
        }));
        const agentToSection = {
          Marketing: "Marketing Strategy",
          Risk: "Risk Assessment",
          Finance: "Financial Model",
          Developer: "Technology Stack",
        };
        if (agentToSection[agent] && data.content) {
          set((s) => ({
            livingDoc: {
              ...s.livingDoc,
              [agentToSection[agent]]: data.content,
            },
          }));
        }
        break;
      }

      case "consensus_update":
        set({ consensusScore: data.score });
        break;

      case "consensus_reached":
        // Mark convergence — do NOT jump to results
        set({ converged: true, consensusScore: data.final_score });
        break;

      case "final_plan":
        // Plan ready — do NOT jump to results, just show CTA
        set((s) => ({
          finalPlan: data.plan,
          livingDoc: { ...s.livingDoc, ...data.plan },
          planReady: true,
          agentStates: { ...s.agentStates, Synthesis: { status: "complete" } },
        }));
        break;

      case "pdf_ready":
        set({ pdfReady: true });
        break;

      case "deployment_complete":
        set({ deploymentUrl: data.url || "" });
        break;

      case "system_done":
        // Simulation finished — do NOT jump to results
        set({ simulationDone: true });
        break;

      default:
        break;
    }
  },

  startSimulation: () =>
    set({
      stage: "active",
      phase: 1,
      livingDoc: {},
      agentStates: {},
      feed: [],
      consensusScore: 0,
      converged: false,
      finalPlan: null,
      planReady: false,
      simulationDone: false,
      pdfReady: false,
      deploymentUrl: "",
    }),

  stopSimulation: () => set({ simulationDone: true }),
}));
