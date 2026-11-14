import type { Config } from "tailwindcss";

// Clean industrial (CP0): light neutral, one teal accent, red = alerts, mono part numbers.
export default {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        surface: "var(--surface)",
        ink: "var(--ink)",
        muted: "var(--muted)",
        line: "var(--line)",
        accent: { DEFAULT: "var(--accent)", soft: "var(--accent-soft)" },
        alert: { DEFAULT: "var(--alert)", soft: "var(--alert-soft)" },
        warn: { DEFAULT: "var(--warn)", soft: "var(--warn-soft)" },
        ok: "var(--ok)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
