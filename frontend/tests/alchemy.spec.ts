import { test, expect } from "@playwright/test";

const backend = "http://127.0.0.1:8011";

test.beforeEach(async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/herbs`);
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    await route.fulfill({ response: await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search }) });
  });
});

test("crafts one pill from three herbs and a replay does not mint another", async ({ page, request }) => {
  await page.goto("/#alchemy");
  await expect(page.getByRole("heading", { name: "Luyện Đan" })).toBeVisible();
  const summary = page.locator(".equipment-summary");
  await expect(page.getByText("3 Vân Linh Thảo")).toBeVisible();
  await expect(summary.getByText("Vân Linh Thảo", { exact: true }).locator("..")).toContainText("3");
  const pills = summary.getByText("Tụ Khí Đan", { exact: true }).locator("..");
  const before = await pills.locator("strong").innerText();
  let sent: { request_id: string; recipe_key: string; ingredient_quantity: number } | undefined;
  page.on("request", req => {
    if (req.url().includes("/alchemy/craft") && req.method() === "POST") sent = req.postDataJSON();
  });
  await page.getByRole("button", { name: "Luyện" }).click();
  await expect(pills.locator("strong")).toHaveText(String(Number(before) + 1));
  await expect(summary.getByText("Vân Linh Thảo", { exact: true }).locator("..")).toContainText("0");
  await page.reload();
  await expect(page.locator(".equipment-summary").getByText("Tụ Khí Đan", { exact: true }).locator("..")).toContainText(String(Number(before) + 1));
  const replay = await request.post(`${backend}/alchemy/craft`, { data: sent });
  expect(replay.ok()).toBeTruthy();
  await page.reload();
  const after = page.locator(".equipment-summary");
  await expect(after.getByText("Tụ Khí Đan", { exact: true }).locator("..")).toContainText(String(Number(before) + 1));
  await expect(after.getByText("Vân Linh Thảo", { exact: true }).locator("..")).toContainText("0");
});

test("alchemy price, herb count and result stay readable on desktop, mobile and keyboard", async ({ page }) => {
  await page.goto("/#alchemy");
  const craft = page.getByRole("button", { name: "Luyện" });
  await craft.focus();
  await craft.press("Enter");
  await expect(page.locator(".equipment-summary").getByText("Vân Linh Thảo", { exact: true }).locator("..")).toContainText("0");
  for (const width of [1440, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page.getByText("Giá luyện", { exact: true })).toBeVisible();
    await expect(page.getByText("Vân Linh Thảo", { exact: true }).first()).toBeVisible();
    await expect(page.getByText("Tụ Khí Đan", { exact: true }).first()).toBeVisible();
  }
});
