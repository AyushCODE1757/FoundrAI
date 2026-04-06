// "use client";
// import { useCallback, useRef, useEffect } from "react";
// import { useAppStore } from "@/store/useAppStore";

// const API = process.env.NEXT_PUBLIC_API_URL;

// export function useSimulation() {
//   const { idea, fastMode, handleEvent, startSimulation, stopSimulation } =
//     useAppStore();

//   const run = useCallback(async () => {
//     if (!idea.trim()) return;
//     startSimulation();
//     try {
//       const res = await fetch(`${API}/simulate`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ idea, fast: fastMode }),
//       });
//       if (!res.ok) throw new Error("Network error");
//       const reader = res.body.getReader();
//       const dec = new TextDecoder();
//       let buf = "";
//       while (true) {
//         const { done, value } = await reader.read();
//         if (done) break;
//         buf += dec.decode(value, { stream: true });
//         const chunks = buf.split("\n\n");
//         buf = chunks.pop() || "";
//         for (const chunk of chunks) {
//           if (chunk.startsWith("data: ")) {
//             try {
//               handleEvent(JSON.parse(chunk.slice(6)));
//             } catch {}
//           }
//         }
//       }
//     } catch (e) {
//       console.error(e);
//     } finally {
//       stopSimulation();
//     }
//   }, [idea, fastMode, handleEvent, startSimulation, stopSimulation]);

//   return { run };
// }

// export function useAutoScroll(dep) {
//   const ref = useRef(null);
//   useEffect(() => {
//     if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
//   }, [dep]);
//   return ref;
// }

"use client";
import { useCallback, useRef, useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";

const API = "http://localhost:8000";

// Delay between processing each SSE event (ms)
// Makes the simulation feel deliberate instead of instant
const EVENT_DELAY_MS = 800;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function useSimulation() {
  const { idea, fastMode, handleEvent, startSimulation, stopSimulation } =
    useAppStore();

  const run = useCallback(async () => {
    if (!idea.trim()) return;
    startSimulation();
    try {
      const res = await fetch(`${API}/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea, fast: fastMode }),
      });
      if (!res.ok) throw new Error("Network error");

      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const chunks = buf.split("\n\n");
        buf = chunks.pop() || "";

        for (const chunk of chunks) {
          if (chunk.startsWith("data: ")) {
            try {
              const evt = JSON.parse(chunk.slice(6));
              handleEvent(evt);
              // Skip delay for non-visual events
              const skipDelay = [
                "ping",
                "consensus_update",
                "system_done",
                "pdf_ready",
              ].includes(evt.type);
              if (!skipDelay) await sleep(EVENT_DELAY_MS);
            } catch {}
          }
        }
      }
    } catch (e) {
      console.error("Stream error:", e);
    } finally {
      stopSimulation();
    }
  }, [idea, fastMode, handleEvent, startSimulation, stopSimulation]);

  return { run };
}

export function useAutoScroll(dep) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
    }
  }, [dep]);
  return ref;
}
