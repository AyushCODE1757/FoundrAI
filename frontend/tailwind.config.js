/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
    "./lib/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0f",
        surface: "#12121a",
        surface2: "#1a1a26",
        ceo: "#6366f1",
        marketing: "#f59e0b",
        risk: "#ef4444",
        finance: "#10b981",
        developer: "#3b82f6",
        strategist: "#8b5cf6",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        fira: ["Fira Code", "monospace"],
      },
    },
  },
  plugins: [],
};
