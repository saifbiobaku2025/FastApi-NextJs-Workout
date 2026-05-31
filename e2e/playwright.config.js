const { defineConfig } = require("@playwright/test");
const path = require("path");

const repoRoot = path.join(__dirname, "..");
const composeFile = path.join(repoRoot, "docker-compose.e2e.yml");
const composeHostFile = path.join(repoRoot, "docker-compose.e2e.host.yml");
const envFile = path.join(repoRoot, ".env.e2e");
const inDocker = !!process.env.E2E_DOCKER;

module.exports = defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.js",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [["html", { open: "never" }], ["list"]],
  use: {
    baseURL: process.env.BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  ...(inDocker
    ? {}
    : {
        webServer: {
          command: `docker compose -f ${composeFile} -f ${composeHostFile} --env-file ${envFile} up --build`,
          url: "http://localhost:3000",
          reuseExistingServer: !process.env.CI,
          timeout: 180_000,
          cwd: repoRoot,
        },
      }),
});
