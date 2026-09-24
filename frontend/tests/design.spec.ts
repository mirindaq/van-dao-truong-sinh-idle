import { test, expect } from "@playwright/test";

const backend = "http://127.0.0.1:8011";
const screens = [
  ["home", "Động Phủ"], ["cultivation", "Tĩnh tâm tu luyện"],
  ["character", "Nhân Vật"], ["skills", "Công Pháp"],
  ["equipment", "Trang Bị"], ["inventory", "Túi Đồ"],
  ["alchemy", "Luyện Đan"], ["pets", "Linh Thú"],
  ["partner", "Đạo Lữ"], ["exploration", "Thám Hiểm"],
  ["world", "Thiên Hạ"], ["rift", "Bí Cảnh"], ["journal", "Nhật Ký"],
];

test.beforeEach(async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/existing`);
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    await route.fulfill({ response: await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search }) });
  });
});

for (const width of [320, 390, 768, 1440]) {
  test(`paper design: all destinations fit ${width}px with loaded artwork`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/");
    for (const [id, title] of screens) {
      await page.evaluate(hash => { location.hash = hash; }, id);
      await expect(page.getByRole("heading", { level: 1, name: title, exact: true })).toBeVisible();
      if (id === "alchemy") await expect(page.getByRole("heading", { name: "Mẻ Tụ Khí Đan" })).toBeVisible();
      if (id === "partner") await expect(page.getByRole("button", { name: "Kết duyên Diệp Thanh Trúc" })).toBeVisible();
      if (id === "pets") await expect(page.getByRole("heading", { name: "Thanh Xà" })).toBeVisible();
      await expect.poll(() => page.evaluate(() => [...document.images].every(img => img.complete && img.naturalWidth > 0))).toBe(true);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${id} overflow at ${width}px`).toBe(true);
      expect(await page.evaluate(() => getComputedStyle(document.documentElement).colorScheme)).toBe("light");
    }
    expect(errors).toEqual([]);
  });
}

test("home links show open features and keyboard settings preserve reduced motion", async ({ page }) => {
  await page.goto("/");
  const routes = page.locator(".opportunities");
  await expect(routes).not.toContainText("Chưa mở");
  await routes.getByRole("link", { name: /Vào đan phòng/ }).click();
  await expect(page.getByRole("heading", { name: "Luyện Đan", exact: true })).toBeVisible();
  const settings = page.getByRole("button", { name: "Cài đặt", exact: true });
  await settings.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("dialog", { name: "Cài đặt" })).toBeVisible();
  await page.getByRole("checkbox", { name: "Giảm chuyển động" }).check();
  await expect(page.locator("html")).toHaveAttribute("data-reduce-motion", "true");
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(settings).toBeFocused();
  await page.getByRole("button", { name: "Thu gọn thanh bên" }).click();
  await expect(page.getByRole("navigation", { name: "Tiên lộ" }).getByRole("link", { name: "Động Phủ", exact: true })).toBeVisible();
});
