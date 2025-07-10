/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fee5e5',
          100: '#fcc5c5',
          200: '#fa9a9a',
          300: '#f76e6e',
          400: '#f44d4d',
          500: '#ED1C24', // State Farm primary red
          600: '#d11920',
          700: '#a9141a',
          800: '#891116',
          900: '#6d0e12',
        },
        statefarm: {
          red: '#ED1C24',
          darkred: '#B71C1C',
          lightgray: '#F5F5F5',
          gray: '#757575',
          darkgray: '#333333',
        }
      },
      fontFamily: {
        sans: ['Nunito', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}