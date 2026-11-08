/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        studio: {
          950: '#0B0D10',
          900: '#101317',
          850: '#15191F',
          800: '#1C2129',
          700: '#282F3B',
          600: '#3D4656'
        },
        cyan: {
          DEFAULT: '#00D9FF',
          accent: '#00D9FF'
        },
        violet: {
          accent: '#A55EEA'
        },
        amber: {
          highlight: '#FED330'
        }
      }
    },
  },
  plugins: [],
}

