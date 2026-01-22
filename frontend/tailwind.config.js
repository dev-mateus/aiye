export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Verde mata/natureza - primário
        "umbanda-primary": "#2D5016",
        "umbanda-forest": "#4A7C59",
        
        // Dourado/âmbar - sagrado
        "umbanda-gold": "#D4AF37",
        "umbanda-amber": "#DAA520",
        
        // Terra/barro - terreiro
        "umbanda-earth": "#8B4513",
        "umbanda-clay": "#A0826D",
        
        // Marfim/búzios - luz
        "umbanda-light": "#FFF8DC",
        "umbanda-ivory": "#FFFFF0",
        
        // Roxo/místico - orixá
        "umbanda-purple": "#663399",
        
        // Neutros naturais
        "umbanda-sand": "#F5F5DC",
        "umbanda-dark": "#2C2416",
        "umbanda-text": "#3D3D3D",
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
