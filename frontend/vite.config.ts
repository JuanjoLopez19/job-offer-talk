import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");

  return {
    base: env.VITE_BASE_PATH || "/",
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
