/**
 * Symphony-IR Tailwind CSS Configuration
 *
 * Maps design tokens from gui/design_tokens.py to Tailwind utility classes.
 * Use with the Tailwind CLI or a bundler (Vite, Next.js, etc.) for web frontends.
 *
 * Install: npm install -D tailwindcss
 * Build:   npx tailwindcss -i ./src/input.css -o ./styles/tailwind.css
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,js,jsx,ts,tsx}",
    "./templates/**/*.html",
    "./gui/**/*.py",
  ],

  darkMode: "media",   // Respects prefers-color-scheme; use "class" for manual toggle

  theme: {
    extend: {

      // ── Brand Colors ─────────────────────────────────────────────────────
      colors: {
        primary: {
          DEFAULT: "#3B82F6",    // blue-500
          light:   "#93C5FD",    // blue-300
          dark:    "#1D4ED8",    // blue-700
          50:      "#EFF6FF",
          100:     "#DBEAFE",
          200:     "#BFDBFE",
          300:     "#93C5FD",
          400:     "#60A5FA",
          500:     "#3B82F6",
          600:     "#2563EB",
          700:     "#1D4ED8",
          800:     "#1E40AF",
          900:     "#1E3A8A",
        },

        accent: {
          DEFAULT: "#8B5CF6",    // violet-500
          light:   "#C4B5FD",
          dark:    "#6D28D9",
        },

        success: {
          DEFAULT: "#22C55E",
          bg:      "#F0FDF4",
        },
        warning: {
          DEFAULT: "#F59E0B",
          bg:      "#FFFBEB",
        },
        error: {
          DEFAULT: "#EF4444",
          bg:      "#FEF2F2",
        },
        info: {
          DEFAULT: "#06B6D4",
          bg:      "#ECFEFF",
        },

        // Neutral surface tokens
        surface:     "#F8FAFC",
        "surface-alt": "#F1F5F9",
        border:      "#E2E8F0",

        // Dark mode surface tokens (use with dark: prefix)
        "dark-bg":         "#0D1117",
        "dark-surface":    "#161B22",
        "dark-surface-alt":"#21262D",
        "dark-border":     "#30363D",
        "dark-text":       "#E6EDF3",
        "dark-muted":      "#8B949E",
      },

      // ── Typography ───────────────────────────────────────────────────────
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "Fira Code",
          "Cascadia Code",
          "Consolas",
          "Courier New",
          "monospace",
        ],
      },

      fontSize: {
        xs:   ["0.75rem",  { lineHeight: "1rem" }],
        sm:   ["0.875rem", { lineHeight: "1.25rem" }],
        base: ["1rem",     { lineHeight: "1.5rem" }],
        lg:   ["1.125rem", { lineHeight: "1.75rem" }],
        xl:   ["1.25rem",  { lineHeight: "1.75rem" }],
        "2xl": ["1.5rem",  { lineHeight: "2rem" }],
        "3xl": ["1.875rem",{ lineHeight: "2.25rem" }],
        "4xl": ["2.25rem", { lineHeight: "2.5rem" }],
      },

      // ── Border Radius ────────────────────────────────────────────────────
      borderRadius: {
        none:  "0",
        sm:    "0.25rem",
        DEFAULT: "0.375rem",
        md:    "0.5rem",
        lg:    "0.75rem",
        xl:    "1rem",
        "2xl": "1.5rem",
        full:  "9999px",
      },

      // ── Box Shadows ──────────────────────────────────────────────────────
      boxShadow: {
        sm:     "0 1px 2px 0 rgba(0,0,0,0.05)",
        DEFAULT:"0 1px 3px 0 rgba(0,0,0,0.1), 0 1px 2px -1px rgba(0,0,0,0.1)",
        md:     "0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)",
        lg:     "0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)",
        xl:     "0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)",
        inner:  "inset 0 2px 4px 0 rgba(0,0,0,0.05)",
        none:   "none",
      },

      // ── Transitions ──────────────────────────────────────────────────────
      transitionTimingFunction: {
        DEFAULT: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
      transitionDuration: {
        fast:   "150ms",
        DEFAULT:"200ms",
        slow:   "300ms",
        slower: "500ms",
      },

      // ── Z-Index ──────────────────────────────────────────────────────────
      zIndex: {
        dropdown: "1000",
        sticky:   "1020",
        fixed:    "1030",
        overlay:  "1040",
        modal:    "1050",
        popover:  "1060",
        tooltip:  "1070",
      },

      // ── Animation (keyframes) ────────────────────────────────────────────
      keyframes: {
        "fade-in": {
          "0%":   { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "slide-in": {
          "0%":   { transform: "translateX(-16px)", opacity: "0" },
          "100%": { transform: "translateX(0)",     opacity: "1" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%":      { opacity: "0.6" },
        },
      },
      animation: {
        "fade-in":   "fade-in 200ms ease-out",
        "slide-in":  "slide-in 200ms ease-out",
        "pulse-soft":"pulse-soft 2s ease-in-out infinite",
      },
    },
  },

  plugins: [
    // Uncomment when installed:
    // require("@tailwindcss/forms"),
    // require("@tailwindcss/typography"),
  ],
};
