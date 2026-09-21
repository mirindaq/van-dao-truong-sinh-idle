import { test, expect } from "@playwright/test";

const backend = "http://127.0.0.1:8011";

test.beforeEach(async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/world-offline`);
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    await route.fulfill({ response: await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search }) });
  });
});

test("living world shows NPC profiles, news and persistent return report", async ({ page }) => {
  await page.goto("/#world");
  await expect(page.getByRole("heading", { name: "Thiên Hạ", exact: true })).toBeVisible();
  await expect(page.getByLabel("Trong lúc bạn vắng mặt")).toContainText("12 nhịp");
  await expect(page.getByLabel("Trong lúc bạn vắng mặt")).toContainText(/Bộ luật v\d+ · [0-9a-f]{16}/);
  await expect(page.getByLabel("Trong lúc bạn vắng mặt")).toContainText(/cơ duyên|đột phá|bị thương|bình phục|linh triều|thương đội|khí tức yêu thú/);
  await expect(page.getByRole("button", { name: /Tạ Vô Trần/ })).toBeVisible();
  await page.getByRole("button", { name: /Tạ Vô Trần/ }).click();
  await expect(page.getByRole("heading", { name: "Tạ Vô Trần" })).toBeVisible();
  await page.getByRole("button", { name: "Trở lại Thiên Hạ" }).click();
  await page.getByRole("button", { name: "Thế giới" }).click();
  await expect(page.getByRole("button", { name: "Thế giới" })).toHaveAttribute("aria-pressed", "true");
  await page.evaluate(() => { location.hash = "home"; });
  await expect(page.getByLabel("Trong lúc bạn vắng mặt")).toContainText("XEM THIÊN HẠ");
  await page.getByRole("button", { name: "XEM THIÊN HẠ" }).click();
  await expect(page.getByRole("heading", { name: "Thiên Hạ", exact: true })).toBeVisible();
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await expect(page.getByLabel("Trong lúc bạn vắng mặt")).toBeVisible();
  await page.getByRole("button", { name: "ĐÃ ĐỌC" }).click();
  await expect(page.getByLabel("Trong lúc bạn vắng mặt")).toHaveCount(0);
  await page.reload();
  await expect(page.getByLabel("Trong lúc bạn vắng mặt")).toHaveCount(0);
});

test("world remains usable with keyboard and at mobile widths", async ({ page }) => {
  await page.goto("/#world");
  const firstNpc = page.locator(".npc-card").first();
  await firstNpc.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("heading", { name: "Tạ Vô Trần" })).toBeVisible();
  await page.getByRole("button", { name: "Trở lại Thiên Hạ" }).click();
  for (const width of [390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.screenshot({ path: `test-results/world-${width}.png`, fullPage: true });
  }
  expect(await page.locator(".npc-card img").evaluateAll(images => images.every(image => image instanceof HTMLImageElement && image.complete && image.naturalWidth > 0))).toBe(true);
});

test("world keeps the last snapshot when refresh loses connection", async ({ page }) => {
  await page.goto("/#world");
  await expect(page.getByRole("button", { name: /Lạc Thanh Hàn/ })).toBeVisible();
  await page.route("**/api/world/state", async route => { await route.fetch({ url: `${backend}/world/state` }); await route.abort(); });
  await page.getByRole("button", { name: "Đồng bộ hành trình" }).click();
  await expect(page.getByText("Đang hiển thị lần lưu gần nhất.")).toBeVisible();
  await expect(page.getByRole("button", { name: /Lạc Thanh Hàn/ })).toBeVisible();
  await page.unroute("**/api/world/state");
  await page.getByRole("button", { name: "Đồng bộ hành trình" }).click();
  await expect(page.getByText("Đang hiển thị lần lưu gần nhất.")).toHaveCount(0);
  await expect(page.getByRole("button", { name: /Lạc Thanh Hàn/ })).toBeVisible();
});
