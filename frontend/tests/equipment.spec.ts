import { test, expect } from "@playwright/test";

const backend = "http://127.0.0.1:8011";

test.beforeEach(async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/existing`);
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    await route.fulfill({ response: await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search }) });
  });
});

test("claims the pack once, equips slots and persists combat power", async ({ page }) => {
  await page.goto("/#inventory");
  await expect(page.getByRole("button", { name: "NHẬN TRANG BỊ" })).toBeVisible();
  await page.getByRole("button", { name: "NHẬN TRANG BỊ" }).click();
  await expect(page.getByText("Đã nhận trang bị")).toBeVisible();
  await page.getByRole("button", { name: "Trang bị", exact: true }).first().click();
  await expect(page.getByRole("heading", { name: "Trang Bị" })).toBeVisible();
  await page.getByRole("button", { name: /Mặc Thanh Trúc Kiếm/ }).click();
  await expect(page.getByText("Tổng chiến lực").locator("..")).toContainText("17");
  await page.reload();
  await expect(page.getByRole("heading", { name: "Trang Bị" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Tháo Thanh Trúc Kiếm" })).toBeVisible();
  await page.getByRole("button", { name: "Tháo Thanh Trúc Kiếm" }).click();
  await expect(page.getByText("Tổng chiến lực").locator("..")).toContainText("12");
});

test("equipment layout remains usable on mobile and narrow width", async ({ page }) => {
  await page.goto("/#inventory");
  await page.getByRole("button", { name: "NHẬN TRANG BỊ" }).click();
  await page.getByRole("button", { name: "Trang bị", exact: true }).first().click();
  const keyboardEquip = page.getByRole("button", { name: /Mặc Thanh Trúc Kiếm/ });
  await keyboardEquip.focus();
  await keyboardEquip.press("Enter");
  await expect(page.getByRole("button", { name: "Tháo Thanh Trúc Kiếm" })).toBeVisible();
  await page.getByRole("button", { name: "Tháo Thanh Trúc Kiếm" }).click();
  for (const width of [390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.screenshot({ path: `test-results/equipment-${width}.png`, fullPage: true });
  }
  await expect(page.getByRole("heading", { name: "Ngọc Bội" })).toBeVisible();
  expect(await page.locator("img").evaluateAll(images => images.every(img => (img as HTMLImageElement).complete && (img as HTMLImageElement).naturalWidth > 0))).toBe(true);
});

test("a failed equipment request blocks a second mutation until sync", async ({ page }) => {
  await page.goto("/#inventory");
  await page.getByRole("button", { name: "NHẬN TRANG BỊ" }).click();
  await page.getByRole("button", { name: "Trang bị", exact: true }).first().click();
  await page.route("**/api/equipment/slot", async route => {
    const url = new URL(route.request().url());
    await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search });
    await route.fulfill({ status: 503, json: { detail: "unavailable" } });
  });
  await page.getByRole("button", { name: /Mặc Thanh Trúc Kiếm/ }).click();
  await expect(page.getByRole("status").filter({ hasText: "Chưa xác nhận" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Mặc Thanh Trúc Kiếm/ })).toBeDisabled();
  await page.unroute("**/api/equipment/slot");
  await page.getByRole("button", { name: "Đồng bộ trang bị" }).click();
  await expect(page.getByRole("button", { name: "Tháo Thanh Trúc Kiếm" })).toBeVisible();
  await expect(page.getByText("Tổng chiến lực").locator("..")).toContainText("17");
});
