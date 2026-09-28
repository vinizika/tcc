import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  timeout: 60000,
  expect: { timeout: 15000 },
  workers: 1,
  use: {
    baseURL: process.env.APP_URL || "http://localhost:3000",
    viewport: { width: 1440, height: 960 },
    reducedMotion: "reduce",
    screenshot: "only-on-failure",
  },
});
