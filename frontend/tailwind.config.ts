import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          50: '#FFFDF0',
          100: '#FFF9D6',
          200: '#FFF0A3',
          300: '#FFE566',
          400: '#FFD700',  // Primary gold
          500: '#E6C200',
          600: '#BFA000',
          700: '#997E00',
          800: '#735E00',
          900: '#4D3F00',
        },
        navy: {
          50: '#E8EAF0',
          100: '#C5C9D6',
          200: '#8B91A8',
          300: '#515A7A',
          400: '#2C3654',
          500: '#1A2238',  // Primary navy
          600: '#151C2E',
          700: '#101624',
          800: '#0B101A',
          900: '#060A10',
        },
      },
      fontFamily: {
        serif: ['Georgia', 'Times New Roman', 'serif'],
      },
    },
  },
  plugins: [],
};

export default config;
