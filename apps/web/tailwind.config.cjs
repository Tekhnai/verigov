module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b0f1a",
        slate: "#111827",
        steel: "#1f2937",
        cloud: "#e5e7eb",
        accent: "#f97316"
      },
      fontFamily: {
        display: ["Space Grotesk", "ui-sans-serif", "system-ui"],
        body: ["IBM Plex Sans", "ui-sans-serif", "system-ui"],
      },
      boxShadow: {
        glow: "0 0 40px rgba(249, 115, 22, 0.25)",
      }
    }
  },
  plugins: [],
};
