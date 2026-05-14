/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: {
          50: '#f8fafc',
          900: '#0f172a',
          950: '#020617',
        },
      },
      animation: {
        'pulse-dot': 'pulse 1.4s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
