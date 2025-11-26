export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "umbanda-primary": "#2D5016",
        "umbanda-secondary": "#6BA586",
        "umbanda-accent": "#8B9D6F",
        "umbanda-light": "#E8F1E2",
        "umbanda-warm": "#D4C5B9",
        "umbanda-dark": "#1F2937",
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
