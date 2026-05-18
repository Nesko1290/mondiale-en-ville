/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0B1320",
          900: "#0B1320",
          800: "#111A2B",
          700: "#1B2438",
        },
        cream: {
          DEFAULT: "#F6F1E8",
          50: "#FBF8F3",
          100: "#F6F1E8",
          200: "#EFE8D9",
        },
        sand: {
          DEFAULT: "#C9A876",
          600: "#B8956A",
          500: "#C9A876",
          400: "#D7BC8F",
        },
        muted: "#6B7280",
        line: "#E5E0D5",
        success: "#16A34A",
        warning: "#D97706",
      },
      fontFamily: {
        sans: ["System"],
        serif: ["Georgia"],
      },
      borderRadius: {
        card: "20px",
        pill: "999px",
      },
    },
  },
  plugins: [],
};
