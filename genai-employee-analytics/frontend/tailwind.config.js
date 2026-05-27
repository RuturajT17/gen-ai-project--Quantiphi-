module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["Manrope", "sans-serif"],
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" },
        },
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        glow: {
          "0%, 100%": { boxShadow: "0 0 0 rgba(14, 165, 233, 0)" },
          "50%": { boxShadow: "0 0 24px rgba(14, 165, 233, 0.35)" },
        },
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        "fade-up": "fadeUp 0.7s ease-out both",
        glow: "glow 3s ease-in-out infinite",
      },
      backgroundImage: {
        "radial-soft": "radial-gradient(circle at top, rgba(59, 130, 246, 0.18), transparent 55%)",
      },
    },
  },
  plugins: [],
};
