import { test, expect, type Page } from "@playwright/test";

const backend = "http://127.0.0.1:8011";

test.beforeEach(async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/existing`);
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    await route.fulfill({ response: await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search }) });
  });
});

async function runningAnimations(page: Page) {
  return page.evaluate(() => document.getAnimations().filter(a => a.playState === "running").length);
}

test("reduced motion setting leaves no running animation around a modal", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1, name: "Động Phủ", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Cài đặt", exact: true }).click();
  await page.getByRole("checkbox", { name: "Giảm chuyển động" }).check();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.getByRole("button", { name: "Cài đặt", exact: true }).click();
  await expect(page.getByRole("dialog", { name: "Cài đặt" })).toBeVisible();
  expect(await runningAnimations(page)).toBe(0);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  expect(await runningAnimations(page)).toBe(0);
});

test("operating system reduced motion is the default and the setting can override it", async ({ browser, baseURL }) => {
  const context = await browser.newContext({ reducedMotion: "reduce", baseURL });
  const page = await context.newPage();
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    await route.fulfill({ response: await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search }) });
  });
  await page.goto("/");
  await expect(page.locator("html")).toHaveAttribute("data-reduce-motion", "true");
  await page.getByRole("button", { name: "Cài đặt", exact: true }).click();
  const setting = page.getByRole("checkbox", { name: "Giảm chuyển động" });
  await expect(setting).toBeChecked();
  await setting.uncheck();
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-reduce-motion", "false");
  await context.close();
});

async function recordViewTransitions(page: Page) {
  await page.addInitScript(() => {
    const record = window as unknown as { __vt: number[] };
    record.__vt = [];
    const original = document.startViewTransition?.bind(document);
    if (!original) return;
    document.startViewTransition = ((arg: Parameters<typeof original>[0]) => {
      const transition = original(arg);
      transition.ready.then(() => {
        record.__vt.push(document.getAnimations().filter(a => (a.effect as KeyframeEffect | null)?.pseudoElement?.startsWith("::view-transition")).length);
      }, () => record.__vt.push(-1));
      return transition;
    }) as typeof document.startViewTransition;
  });
}

async function openSkillsFromHome(page: Page) {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1, name: "Động Phủ", exact: true })).toBeVisible();
  await page.evaluate(() => { location.hash = "skills"; });
  await expect(page.getByRole("heading", { level: 1, name: "Công Pháp", exact: true })).toBeVisible();
}

test("changing screens runs a view transition when motion is on", async ({ page }) => {
  await recordViewTransitions(page);
  await openSkillsFromHome(page);
  await expect.poll(() => page.evaluate(() => (window as unknown as { __vt: number[] }).__vt)).toContainEqual(expect.any(Number));
  const counts = await page.evaluate(() => (window as unknown as { __vt: number[] }).__vt);
  expect(Math.max(...counts)).toBeGreaterThan(0);
});

test("changing screens runs no view transition with reduced motion", async ({ page }) => {
  await recordViewTransitions(page);
  await page.addInitScript(() => localStorage.setItem("reduce-motion", "true"));
  await openSkillsFromHome(page);
  await page.evaluate(() => { location.hash = "journal"; });
  await expect(page.getByRole("heading", { level: 1, name: "Nhật Ký", exact: true })).toBeVisible();
  expect(await page.evaluate(() => (window as unknown as { __vt: number[] }).__vt)).toEqual([]);
  expect(await runningAnimations(page)).toBe(0);
});
