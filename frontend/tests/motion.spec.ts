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

test("seclusion report counts to the server value, skips on tap, and does not replay after reload", async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/offline`);
  const report = (await (await request.get(`${backend}/game/state`)).json()).offline_report;
  const final = "+" + new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 2 }).format(report.earned_exp);
  await page.goto("/");
  const dialog = page.getByRole("dialog", { name: "Bế Quan Kết Thúc" });
  const counter = dialog.locator(".offline-reward strong");
  await expect(dialog).toContainText("8 giờ");
  await dialog.locator(".seclusion-report").click();
  await expect(counter).toHaveText(final, { timeout: 300 });
  await page.reload();
  await expect(dialog).toBeVisible();
  await expect(counter).toHaveText(final, { timeout: 300 });
  await page.getByRole("button", { name: "XUẤT QUAN" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("seclusion report shows final numbers at once with reduced motion", async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/offline`);
  const report = (await (await request.get(`${backend}/game/state`)).json()).offline_report;
  await page.addInitScript(() => localStorage.setItem("reduce-motion", "true"));
  await page.goto("/");
  const dialog = page.getByRole("dialog", { name: "Bế Quan Kết Thúc" });
  await expect(dialog).toBeVisible();
  const counter = dialog.locator(".offline-reward strong");
  await expect(counter).toHaveText("+" + new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 2 }).format(report.earned_exp), { timeout: 300 });
  expect(await page.locator("canvas").count()).toBe(0);
});

async function attemptBreakthrough(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: "ĐỘT PHÁ", exact: true }).click();
  await page.getByRole("checkbox").check();
  await expect(page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" })).toBeEnabled();
  await page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" }).click();
}

test("breakthrough success plays a skippable ceremony with particles, Escape skips without closing", async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/success`);
  await attemptBreakthrough(page);
  const dialog = page.getByRole("dialog", { name: "Đột phá thành công" });
  await expect(dialog.getByRole("button", { name: "Bỏ qua nghi thức đột phá" })).toBeVisible();
  await expect(dialog.locator("canvas.moment-canvas")).toHaveCount(1);
  await page.keyboard.press("Escape");
  await expect(dialog.getByRole("button", { name: "Bỏ qua nghi thức đột phá" })).toHaveCount(0);
  await expect(dialog).toContainText("Tụ Khí Đan đã dùng1");
  await dialog.getByRole("button", { name: "TIẾP TỤC TIÊN LỘ" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("breakthrough failure plays a quieter ceremony without particles and a tap skips it", async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/failure`);
  await attemptBreakthrough(page);
  const dialog = page.getByRole("dialog", { name: "Đột phá thất bại" });
  const skip = dialog.getByRole("button", { name: "Bỏ qua nghi thức đột phá" });
  await expect(skip).toHaveClass(/failure/);
  await expect(dialog.locator("canvas")).toHaveCount(0);
  await skip.click();
  await expect(dialog).toContainText("Tụ Khí Đan đã dùng1");
});

test("breakthrough result appears at once with reduced motion", async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/success`);
  await page.addInitScript(() => localStorage.setItem("reduce-motion", "true"));
  await attemptBreakthrough(page);
  const dialog = page.getByRole("dialog", { name: "Đột phá thành công" });
  await expect(dialog).toContainText("Tụ Khí Đan đã dùng1");
  await expect(dialog.getByRole("button", { name: "Bỏ qua nghi thức đột phá" })).toHaveCount(0);
  await expect(dialog.locator("canvas")).toHaveCount(0);
  expect(await runningAnimations(page)).toBe(0);
});

test("cave abode cultivation keeps flowing between syncs without passing the stage requirement", async ({ page }) => {
  await page.goto("/");
  const bar = page.getByRole("region", { name: "Động phủ tu luyện" }).getByRole("progressbar", { name: "Tu vi tích lũy" });
  const read = async () => Number(await bar.getAttribute("aria-valuenow"));
  const max = Number(await bar.getAttribute("aria-valuemax"));
  const first = await read();
  await expect.poll(read, { timeout: 4000 }).toBeGreaterThan(first);
  expect(await read()).toBeLessThanOrEqual(max);
  await expect(page.locator(".opportunities")).toContainText("Đột phá");
  await expect(page.locator(".opportunities")).toContainText("Vào đan phòng");
});

test("cave abode stops its ambient motion with reduced motion but still updates the number", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("reduce-motion", "true"));
  await page.goto("/");
  const bar = page.getByRole("region", { name: "Động phủ tu luyện" }).getByRole("progressbar", { name: "Tu vi tích lũy" });
  const first = Number(await bar.getAttribute("aria-valuenow"));
  await expect.poll(async () => Number(await bar.getAttribute("aria-valuenow")), { timeout: 4000 }).toBeGreaterThan(first);
  expect(await runningAnimations(page)).toBe(0);
});
