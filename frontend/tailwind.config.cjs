/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#020817',
        foreground: '#E5E7EB',
        primary: {
          DEFAULT: '#22C55E',
          foreground: '#020617'
        },
        muted: {
          DEFAULT: '#111827',
          foreground: '#9CA3AF'
        },
        card: {
          DEFAULT: '#020617',
          foreground: '#E5E7EB'
        }
      }
    }
  },
  plugins: []
};

