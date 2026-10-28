import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
  },
  test: {
    environment: "jsdom",
    // Placeholders, so auth.js loads in tests and CI without a .env.
    env: {
      VITE_AUTH0_DOMAIN: "test.auth0.example",
      VITE_AUTH0_CLIENT_ID: "test-client-id",
      VITE_AUTH0_AUDIENCE: "https://test-api.example",
    },
  },
});
