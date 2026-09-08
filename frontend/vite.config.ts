import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  const isGitHubPages = env.VITE_GITHUB_PAGES === "true";

  return {
    base: isGitHubPages ? "/job-offer-talk/" : "/",
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        "/v1": {
          target: "http://127.0.0.1:8000",
          ws: true,
        },
      },
    },
    test: {
      environment: "jsdom",
    },
  };
});
