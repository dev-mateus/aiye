export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Backgrounds escuros (Oxossi/Obá - floresta sagrada)
        'umbanda-bg': '#0a1410',
        'umbanda-bg-light': '#111d17',
        'umbanda-dark': '#1a2e1a',
        'umbanda-darker': '#0d1a0d',
        
        // Verde floresta (primário)
        'umbanda-primary': '#4a7c59',
        'umbanda-forest': '#5a9d6a',
        'umbanda-accent': '#7cb97f',
        'umbanda-light': '#8fd191',
        
        // Dourado sagrado
        'umbanda-gold': '#D4AF37',
        'umbanda-amber': '#DAA520',
        
        // Textos
        'umbanda-text': '#e8f5e9',
        'umbanda-text-muted': '#b0c4b1',
        
        // Bordas e cards
        'umbanda-border': '#2d4a2d',
        'umbanda-card': '#151f19',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
