// // "use client";
// // import { useAppStore } from "@/store/useAppStore";

// // export default function ApprovalModal() {
// //   const { showApprovalModal, consensusScore, idea, setShowApprovalModal } =
// //     useAppStore();
// //   if (!showApprovalModal) return null;

// //   const projectName =
// //     idea
// //       .split(" ")
// //       .slice(0, 3)
// //       .join("-")
// //       .toLowerCase()
// //       .replace(/[^a-z0-9-]/g, "") || "my-startup";

// //   const handleApprove = () => {
// //     setShowApprovalModal(false);
// //   };

// //   return (
// //     <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
// //       <div className="animate-scale-up w-full max-w-md rounded-2xl border border-indigo-500/40 bg-[#12121a] shadow-2xl shadow-indigo-500/20 p-8">
// //         <div className="text-center mb-6">
// //           <div className="text-4xl mb-3">✅</div>
// //           <h2 className="text-xl font-bold text-white mb-2">
// //             Business Plan Validated
// //           </h2>
// //           <div className="text-3xl font-extrabold text-indigo-400 mb-2">
// //             {consensusScore.toFixed(1)} / 10.0
// //           </div>
// //           <p className="text-slate-400 text-sm">
// //             All agents have reached consensus
// //           </p>
// //         </div>

// //         <div className="rounded-xl bg-white/[0.04] border border-white/[0.08] p-4 mb-6 space-y-2">
// //           <p className="text-[11px] text-slate-500 font-semibold tracking-widest mb-3 font-fira">
// //             THE DEV AGENT IS READY TO:
// //           </p>
// //           {[
// //             `→ Generate docker-compose.yml, README.md, folder structure`,
// //             `→ Create private GitHub repo: "${projectName}"`,
// //             `→ Push initial commit with starter kit`,
// //           ].map((line, i) => (
// //             <p key={i} className="text-sm text-slate-300 font-fira">
// //               {line}
// //             </p>
// //           ))}
// //         </div>

// //         <div className="flex gap-3">
// //           <button
// //             onClick={() => setShowApprovalModal(false)}
// //             className="flex-1 py-3 rounded-xl border border-white/[0.1] text-slate-400 hover:text-white text-sm font-semibold transition-all"
// //           >
// //             Cancel
// //           </button>
// //           <button
// //             onClick={handleApprove}
// //             className="flex-[2] py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm transition-all shadow-lg shadow-indigo-500/30"
// //           >
// //             ✅ Approve Deployment
// //           </button>
// //         </div>
// //       </div>
// //     </div>
// //   );
// // }

// "use client";
// import { useState } from "react";
// import { GitBranch, Loader2 } from "lucide-react";
// import { useAppStore } from "@/store/useAppStore";

// export default function ApprovalModal() {
//   const { showApprovalModal, consensusScore, idea, setShowApprovalModal } =
//     useAppStore();

//   // Derive a default repo name from the idea
//   const defaultName =
//     idea
//       .toLowerCase()
//       .replace(/[^a-z0-9\s-]/g, "")
//       .trim()
//       .split(/\s+/)
//       .slice(0, 4)
//       .join("-") || "my-startup";

//   const [repoName, setRepoName] = useState(defaultName);
//   const [deploying, setDeploying] = useState(false);
//   const [repoUrl, setRepoUrl] = useState("");
//   const [error, setError] = useState("");

//   if (!showApprovalModal) return null;

//   const handleApprove = async () => {
//     if (!repoName.trim()) return;
//     setDeploying(true);
//     setError("");
//     try {
//       // ── BACKEND CALL ─────────────────────────────────────────────────────
//       // POST http://localhost:8000/approve-deploy
//       // body: { repoName, idea, plan: finalPlan }
//       // response: { url: "https://github.com/org/repo" }
//       // ─────────────────────────────────────────────────────────────────────
//       const res = await fetch("http://localhost:8000/approve-deploy", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({
//           repo_name: repoName.trim(),
//           idea,
//           plan: useAppStore.getState().finalPlan,
//         }),
//       });

//       if (!res.ok) {
//         const data = await res.json().catch(() => ({}));
//         throw new Error(data.detail || `HTTP ${res.status}`);
//       }

//       const data = await res.json();
//       const url = data.repo_url || `https://github.com/your-org/${repoName}`;

//       useAppStore.getState().handleEvent({ type: "deployment_complete", url });
//       setRepoUrl(url);
//       setTimeout(() => setShowApprovalModal(false), 1800);
//     } catch (err) {
//       setError(err.message || "Deployment failed. Check backend logs.");
//     } finally {
//       setDeploying(false);
//     }
//   };

//   // Sanitize repo name as user types
//   const handleRepoInput = (val) => {
//     const clean = val
//       .toLowerCase()
//       .replace(/[^a-z0-9-]/g, "-")
//       .replace(/-+/g, "-")
//       .replace(/^-/, "");
//     setRepoName(clean);
//   };

//   return (
//     <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
//       <div className="animate-scale-up w-full max-w-lg rounded-2xl border border-indigo-500/40 bg-[#12121a] shadow-2xl shadow-indigo-500/20 p-8">
//         {/* Header */}
//         <div className="text-center mb-6">
//           <div className="text-4xl mb-3">✅</div>
//           <h2 className="text-xl font-bold text-white mb-2">
//             Business Plan Validated
//           </h2>
//           <div className="text-3xl font-extrabold text-indigo-400 mb-1">
//             {consensusScore.toFixed(1)}{" "}
//             <span className="text-base text-slate-500 font-normal">/ 10.0</span>
//           </div>
//           <p className="text-slate-500 text-sm">All agents reached consensus</p>
//         </div>

//         {/* What will happen */}
//         <div className="rounded-xl bg-white/[0.03] border border-white/[0.07] p-4 mb-5 space-y-1.5">
//           <p className="text-[10px] text-slate-600 font-semibold tracking-widest mb-3 font-fira">
//             THE DEV AGENT WILL:
//           </p>
//           {[
//             "→ Generate docker-compose.yml, README.md, folder structure",
//             `→ Create private GitHub repo: "${repoName || "..."}"`,
//             "→ Push initial commit with complete starter kit",
//           ].map((line, i) => (
//             <p key={i} className="text-sm text-slate-300 font-fira">
//               {line}
//             </p>
//           ))}
//         </div>

//         {/* ── Repo name input ── */}
//         <div className="mb-5">
//           <label className="block text-xs font-semibold text-slate-400 mb-2 tracking-wide">
//             GITHUB REPO NAME
//           </label>
//           <div className="flex items-center gap-2 rounded-xl border border-white/[0.1] bg-white/[0.03] px-4 py-3 focus-within:border-indigo-500/50 transition-colors">
//             <GitBranch size={15} className="text-slate-600 flex-shrink-0" />
//             <span className="text-slate-600 text-sm font-fira">your-org /</span>
//             <input
//               type="text"
//               value={repoName}
//               onChange={(e) => handleRepoInput(e.target.value)}
//               placeholder="my-startup"
//               disabled={deploying}
//               className="flex-1 bg-transparent text-white text-sm font-fira outline-none placeholder-slate-700 min-w-0"
//               autoFocus
//             />
//           </div>
//           <p className="text-[11px] text-slate-600 mt-1.5 font-fira">
//             Only lowercase letters, numbers and hyphens
//           </p>
//         </div>

//         {/* Error */}
//         {error && (
//           <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400 font-fira">
//             ⚠️ {error}
//           </div>
//         )}

//         {/* Success */}
//         {repoUrl && (
//           <div className="mb-4 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400 font-fira">
//             ✅ Repo created:{" "}
//             <a
//               href={repoUrl}
//               target="_blank"
//               rel="noreferrer"
//               className="underline"
//             >
//               {repoUrl}
//             </a>
//           </div>
//         )}

//         {/* Buttons */}
//         <div className="flex gap-3">
//           <button
//             onClick={() => setShowApprovalModal(false)}
//             disabled={deploying}
//             className="flex-1 py-3 rounded-xl border border-white/[0.1] text-slate-400 hover:text-white text-sm font-semibold transition-all disabled:opacity-40"
//           >
//             Cancel
//           </button>
//           <button
//             onClick={handleApprove}
//             disabled={!repoName.trim() || deploying}
//             className="flex-[2] flex items-center justify-center gap-2 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm transition-all shadow-lg shadow-indigo-500/25"
//           >
//             {deploying ? (
//               <>
//                 <Loader2 size={15} className="animate-spin" /> Creating Repo…
//               </>
//             ) : (
//               <>✅ Create Project & Push Code</>
//             )}
//           </button>
//         </div>

//         {/* Flow hint */}
//         <p className="text-center text-[10px] text-slate-700 mt-4 font-fira leading-relaxed">
//           Backend: generate code → GitHub API create repo → git push → return
//           URL
//         </p>
//       </div>
//     </div>
//   );
// }
