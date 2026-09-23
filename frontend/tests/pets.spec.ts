import { test, expect } from "@playwright/test";

const backend = "http://127.0.0.1:8011";

test.beforeEach(async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/existing`);
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    await route.fulfill({ response: await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search }) });
  });
});

async function rateText(page: import("@playwright/test").Page) {
  return page.getByText("Tốc độ tu vi", { exact: true }).locator("..").locator("strong").innerText();
}

test("bonds one pet, rests, reloads, and recalls the bonus", async ({ page }) => {
  await page.goto("/#pets");
  await expect(page.getByRole("heading", { name: "Linh Thú" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Thanh Xà" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Hỏa Hồ" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Vân Tước" })).toBeVisible();
  const plainRate = await rateText(page);
  await page.getByRole("button", { name: "Kết khế ước Thanh Xà" }).click();
  await expect(page.getByText("Thanh Xà đang theo.")).toBeVisible();
  await expect(page.getByText("Từ linh thú", { exact: true }).locator("..")).toContainText("+6");
  await expect.poll(() => rateText(page)).not.toBe(plainRate);
  const activeRate = await rateText(page);
  await page.getByRole("button", { name: "Cho nghỉ" }).click();
  await expect(page.getByText("Thanh Xà đang nghỉ.")).toBeVisible();
  await expect(page.getByText("Từ linh thú", { exact: true }).locator("..")).toContainText("+0");
  await expect.poll(() => rateText(page)).toBe(plainRate);
  await page.reload();
  await expect(page.getByText("Thanh Xà đang nghỉ.")).toBeVisible();
  await expect(page.getByText("Từ linh thú", { exact: true }).locator("..")).toContainText("+0");
  await page.getByRole("navigation", { name: "Tiên lộ" }).getByRole("link", { name: "Động Phủ", exact: true }).click();
  await expect(page.getByText("Thanh Xà · đang nghỉ")).toBeVisible();
  await page.goto("/#pets");
  await page.getByRole("button", { name: "Gọi lại" }).click();
  await expect(page.getByText("Thanh Xà đang theo.")).toBeVisible();
  await expect(page.getByText("Từ linh thú", { exact: true }).locator("..")).toContainText("+6");
  await expect.poll(() => rateText(page)).toBe(activeRate);
});

test("pet name, state, combat and rate stay readable on desktop, mobile and keyboard", async ({ page }) => {
  await page.goto("/#pets");
  const bond = page.getByRole("button", { name: "Kết khế ước Thanh Xà" });
  await bond.focus();
  await bond.press("Enter");
  await expect(page.getByText("Thanh Xà đang theo.")).toBeVisible();
  for (const width of [1440, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page.getByText("Từ linh thú", { exact: true })).toBeVisible();
    await expect(page.getByText("Tốc độ tu vi", { exact: true })).toBeVisible();
    await expect(page.getByText("Hệ số linh thú", { exact: true })).toBeVisible();
    await expect(page.getByText("Lượng mỗi phút", { exact: true })).toBeVisible();
  }
});
