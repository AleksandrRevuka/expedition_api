/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        'neon-cyan': '#00f0ff',
        'neon-purple': '#bf00ff',
        'dark-bg': '#050510',
      },
      boxShadow: {
        'neon-cyan': '0 0 20px rgba(0, 240, 255, 0.5)',
        'neon-purple': '0 0 20px rgba(191, 0, 255, 0.5)',
        'neon-glow': '0 0 30px rgba(0, 240, 255, 0.4), 0 0 60px rgba(191, 0, 255, 0.2)',
      },
      keyframes: {
        'pulse-neon': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        'glow': {
          '0%, 100%': {
            boxShadow: '0 0 20px rgba(0, 240, 255, 0.5)',
          },
          '50%': {
            boxShadow: '0 0 40px rgba(0, 240, 255, 0.8), 0 0 60px rgba(191, 0, 255, 0.4)',
          },
        },
      },
      animation: {
        'pulse-neon': 'pulse-neon 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
