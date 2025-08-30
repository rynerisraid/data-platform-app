import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import Pages from "vite-plugin-pages";
import { resolve } from "path";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    react(),
    Pages({
      dirs: [{ dir: "src/pages", baseRoute: "" }],
      extensions: ["tsx", "jsx"],
      importMode: "sync",
    }),
  ],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  server: {
    hmr: true,
    watch: {
      usePolling: true,
    },
  },
});
