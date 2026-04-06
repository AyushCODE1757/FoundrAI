import "./globals.css";

export const metadata = {
  title: "FoundrAI 2.0 — Autonomous Business Validation Engine",
  description: "Multi-agent AI consensus engine that validates startup ideas",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "Inter, sans-serif" }}>{children}</body>
    </html>
  );
}
