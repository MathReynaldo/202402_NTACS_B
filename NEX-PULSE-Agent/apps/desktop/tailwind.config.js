/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#050A1F',
          surface: '#0B132B',
          accent: '#00F0FF',
          secondary: '#FF003C',
          text: '#E0E6ED'
        }
      }
    },
  },
  plugins: [],
}
