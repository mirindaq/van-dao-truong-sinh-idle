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

test("every control on every screen is at least 24 by 24 pixels at 320px", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 });
  await page.goto("/");
  const small: string[] = [];
  for (const [id, title] of screens) {
    await page.evaluate(hash => { location.hash = hash; }, id);
    await expect(page.getByRole("heading", { level: 1, name: title, exact: true })).toBeVisible();
    await page.waitForLoadState("networkidle");
    const found = await page.evaluate(() => [...document.querySelectorAll<HTMLElement>("button, a[href], input, select, [role=button]")]
      .filter(el => el.checkVisibility() && !el.closest(".skip-link") && !el.matches(".text-link"))
      .map(el => ({ el, box: el.getBoundingClientRect() }))
      .filter(({ box }) => box.width < 24 || box.height < 24)
      .map(({ el, box }) => `${el.tagName.toLowerCase()} "${(el.getAttribute("aria-label") ?? el.textContent ?? "").trim().slice(0, 30)}" ${Math.round(box.width)}x${Math.round(box.height)}`));
    small.push(...found.map(item => `${id}: ${item}`));
  }
  expect(small).toEqual([]);
});

test("focus ring stays visible against the paper background", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1, name: "Động Phủ", exact: true })).toBeVisible();
  await page.keyboard.press("Tab");
  await page.keyboard.press("Tab");
  const ring = await page.evaluate(() => {
    const el = document.activeElement as HTMLElement;
    const style = getComputedStyle(el);
    return { width: parseFloat(style.outlineWidth), style: style.outlineStyle, color: style.outlineColor, who: `${el.tagName}.${el.className} ${el.textContent?.slice(0, 20)}`, visible: el.matches(":focus-visible") };
  });
  expect(ring.style, JSON.stringify(ring)).not.toBe("none");
  expect(ring.width).toBeGreaterThanOrEqual(2);
  const [r, g, b] = ring.color.match(/\d+/g)!.map(Number);
  const lum = (c: number) => { const v = c / 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  const L = 0.2126 * lum(r) + 0.7152 * lum(g) + 0.0722 * lum(b);
  const paper = 0.2126 * lum(0xf5) + 0.7152 * lum(0xf2) + 0.0722 * lum(0xe9);
  expect((paper + 0.05) / (L + 0.05)).toBeGreaterThanOrEqual(3);
});
