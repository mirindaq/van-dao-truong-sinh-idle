import { defineConfig } from "@playwright/test";
import path from "node:path";

const port = Number(process.env.PLAYWRIGHT_PORT ?? 3002);
const baseURL = `http://127.0.0.1:${port}`;

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  timeout: 45000,
  use: {
    baseURL,
    viewport: { width: 1440, height: 900 },
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  webServer: [
    { command: `${process.platform === "win32" ? ".venv\\Scripts\\python.exe" : ".venv/bin/python"} -m uvicorn tests.ui_server:app --host 127.0.0.1 --port 8011`, cwd: path.resolve("../backend"), url: "http://127.0.0.1:8011/health", reuseExistingServer: false },
    { command: `npx next start --hostname 127.0.0.1 --port ${port}`, url: baseURL, reuseExistingServer: false },
  ],
});
