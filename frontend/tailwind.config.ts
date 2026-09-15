import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101312",
        jade: "#1f6f5f",
        parchment: "#d9c69a",
        gold: "#c79b46",
        moon: "#b9c3cc"
      },
      fontFamily: {
        display: ["serif"]
      }
    }
  },
  plugins: []
};

export default config;

