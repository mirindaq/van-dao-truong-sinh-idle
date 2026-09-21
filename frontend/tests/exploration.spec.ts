import { test, expect } from "@playwright/test";
const backend = "http://127.0.0.1:8011";

test.beforeEach(async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/existing`);
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    await route.fulfill({ response: await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search }) });
  });
});

test("exploration resolves, shows battle log and persists after reload", async ({ page }) => {
  await page.goto("/#exploration");
  await expect(page.getByRole("heading", { name: "Thám Hiểm" })).toBeVisible();
  await page.getByRole("button", { name: "BẮT ĐẦU THÁM HIỂM" }).click();
  await expect(page.getByText("KẾT QUẢ ĐÃ LƯU")).toBeVisible();
  await expect(page.getByText(/Bộ luật v\d+ · [0-9a-f]{16}/)).toBeVisible();
  await expect(page.getByText(/Linh Thạch/)).toBeVisible();
  await page.reload();
  await expect(page.getByText("KẾT QUẢ ĐÃ LƯU")).toBeVisible();
  await expect(page.getByText(/Phần thưởng được lưu/)).toBeVisible();
});

test("exploration stays usable on mobile and 320px", async ({ page }) => {
  await page.goto("/#exploration");
  await page.getByRole("button", { name: "BẮT ĐẦU THÁM HIỂM" }).click();
  for (const width of [390, 320]) {
    await page.setViewportSize({ width, height: 844 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.screenshot({ path: `test-results/exploration-${width}.png`, fullPage: true });
  }
});

test("lost exploration response can be recovered from latest run", async ({ page }) => {
  await page.goto("/#exploration");
  await page.route("**/api/exploration/run", async route => {
    const url = new URL(route.request().url());
    await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search });
    await route.fulfill({ status: 503, json: { detail: "unavailable" } });
  });
  await page.getByRole("button", { name: "BẮT ĐẦU THÁM HIỂM" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await page.unroute("**/api/exploration/run");
  await page.getByRole("button", { name: "Đồng bộ hành trình" }).click();
  await expect(page.getByText("KẾT QUẢ ĐÃ LƯU")).toBeVisible();
});
