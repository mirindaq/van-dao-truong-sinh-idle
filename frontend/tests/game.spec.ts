import { test, expect } from "@playwright/test";

const backend = "http://127.0.0.1:8011";

test.beforeEach(async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/empty`);
  // Redirect to the real isolated FastAPI server; no gameplay response is mocked.
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    const path = url.pathname.replace(/^\/api/, "") + url.search;
    const response = await route.fetch({ url: `${backend}${path}` });
    await route.fulfill({ response });
  });
});

test("new game, root reveal, saved refresh and cultivation preview", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await page.getByLabel("Danh xưng của đạo hữu").fill("Lạc Thanh Hàn");
  await page.getByRole("button", { name: "BẮT ĐẦU VẤN ĐẠO" }).click();
  await expect(page.getByRole("dialog", { name: "Trắc Linh Thạch" })).toBeVisible();
  await expect(page.getByRole("dialog")).toContainText("Mộc Linh Căn");
  await page.getByRole("button", { name: "BƯỚC VÀO TIÊN LỘ" }).click();
  await expect(page.getByRole("region", { name: "Động phủ tu luyện" })).toContainText("Lạc Thanh Hàn");
  await page.reload();
  await expect(page.getByRole("region", { name: "Động phủ tu luyện" })).toContainText("Lạc Thanh Hàn");
  await page.getByRole("button", { name: "TU LUYỆN", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Vận chuyển linh khí" })).toBeVisible();
  await page.getByRole("button", { name: "XEM BÌNH CẢNH" }).click();
  await expect(page.getByRole("dialog")).toContainText("86,7%");
  await expect(page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" })).toBeDisabled();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  expect(errors).toEqual([]);
});

for (const outcome of ["success", "failure"]) {
  test(`backend breakthrough ${outcome}, refresh persisted result`, async ({ page, request }) => {
    await request.post(`${backend}/_test/prepare/${outcome}`);
    await page.goto("/");
    await page.getByRole("button", { name: "ĐỘT PHÁ", exact: true }).click();
    await page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" }).click();
    await expect(page.getByRole("heading", { name: outcome === "success" ? "Đột phá thành công" : "Đột phá thất bại", exact: true })).toBeVisible();
    if (outcome === "failure") await expect(page.getByRole("dialog")).toContainText("12");
    await page.getByRole("button", { name: "TIẾP TỤC TIÊN LỘ" }).click();
    await page.reload();
    await expect(page.getByRole("region", { name: "Động phủ tu luyện" })).toContainText(outcome === "success" ? "TẦNG 2" : "TẦNG 1");
  });
}

test("offline report survives reload and acknowledgement is persistent", async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/offline`);
  await page.goto("/");
  await expect(page.getByRole("dialog")).toContainText("8 giờ");
  await page.reload();
  await expect(page.getByRole("dialog", { name: "Bế Quan Kết Thúc" })).toBeVisible();
  await page.getByRole("button", { name: "NHẬN TU VI" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole("heading", { name: "Động Phủ", exact: true })).toBeVisible();
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("mobile navigation, locked content, assets and no horizontal overflow", async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/existing`);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Động Phủ", exact: true })).toBeVisible();
  await page.screenshot({ path: "test-results/home-mobile.png", fullPage: true });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(
    await page
      .locator("img")
      .evaluateAll(images => images.every(img => img instanceof HTMLImageElement && img.complete && img.naturalWidth > 0)),
  ).toBe(true);
  await page.getByRole("button", { name: "Thêm", exact: true }).click();
  await page.getByRole("dialog").getByRole("link", { name: "Linh Thú", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Linh Thú", exact: true })).toBeVisible();
  await expect(page.getByText("Bạn chưa ký khế ước với bất kỳ linh thú nào.")).toBeVisible();
  await page.getByRole("navigation", { name: "Điều hướng chính" }).getByRole("link", { name: "Động Phủ", exact: true }).click();
  for (const width of [320, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
  await page.screenshot({ path: "test-results/home-desktop.png", fullPage: true });
  await page.getByRole("button", { name: "Thu gọn thanh bên" }).click();
  await expect(page.getByRole("button", { name: "Mở thanh bên" })).toBeVisible();
});

test("loading, connection error and retry", async ({ page }) => {
  let release: () => void = () => {};
  const blocked = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/api/game/state", async route => { await blocked; await route.abort(); });
  await page.goto("/");
  await expect(page.getByLabel("Đang tìm lại động phủ")).toBeVisible();
  release();
  await expect(page.getByRole("heading", { name: "Đường về chìm trong sương" })).toBeVisible();
  await page.unroute("**/api/game/state");
  await page.getByRole("button", { name: "THỬ LẠI", exact: true }).click();
  await expect(page.getByLabel("Danh xưng của đạo hữu")).toBeVisible();
});
