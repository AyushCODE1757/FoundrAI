"use client";
import { useAppStore } from "@/store/useAppStore";
import Navbar from "@/components/layout/Navbar";
import LandingStage from "@/components/landing/LandingStage";
import ActiveStage from "@/components/active/ActiveStage";
import ResultsStage from "@/components/results/ResultsStage";

export default function Home() {
  const { stage } = useAppStore();

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Navbar />
      <div className="pt-14">
        {stage === "landing" && <LandingStage />}
        {stage === "active" && <ActiveStage />}
        {stage === "results" && <ResultsStage />}
      </div>
    </div>
  );
}
