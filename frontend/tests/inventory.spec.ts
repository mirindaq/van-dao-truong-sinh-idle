import { test, expect, type Page } from "@playwright/test";

const backend = "http://127.0.0.1:8011";
async function forward(page: Page) {
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    await route.fulfill({ response: await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search }) });
  });
}
async function openPreview(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: "ĐỘT PHÁ", exact: true }).click();
}
async function choosePill(page: Page) {
  await page.getByRole("checkbox").check();
  await expect(page.getByRole("dialog")).toContainText("95%");
  await expect(page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" })).toBeEnabled();
}
test.beforeEach(async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/success`);
  await forward(page);
});

test("inventory filters, responsive layout, images and keyboard modal", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", e => errors.push(e.message));
  await page.goto("/#inventory");
  await expect(page.getByRole("article", { name: "Tụ Khí Đan" })).toContainText("Số lượng: 3");
  await expect(page.getByRole("article", { name: "Thanh Mộc Quyết" })).toContainText("Số lượng: 1");
  await page.getByRole("button", { name: "Công Pháp", exact: true }).click();
  await expect(page.getByRole("article")).toHaveCount(1);
  await page.getByRole("button", { name: "Tất Cả", exact: true }).click();
  for (const width of [1440, 390, 320]) {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect.poll(() => page.locator("img").evaluateAll(images => images.every(img => (img as HTMLImageElement).complete && (img as HTMLImageElement).naturalWidth > 0))).toBe(true);
    await page.screenshot({ path: `../.ai/2026-09-16-phase-two-items/inventory-${width}.png`, fullPage: true });
  }
  await page.getByRole("button", { name: "Tu luyện", exact: true }).click();
  await page.getByRole("button", { name: "ĐỘT PHÁ", exact: true }).click();
  await choosePill(page);
  await page.keyboard.press("Tab");
  expect(await page.getByRole("dialog").evaluate(dialog => dialog.contains(document.activeElement))).toBe(true);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  expect(errors).toEqual([]);
});

for (const outcome of ["success", "failure"]) {
  test(`pill ${outcome} consumes once and survives fresh browser storage`, async ({ page, request, browser }) => {
    await request.post(`${backend}/_test/prepare/${outcome}`);
    await openPreview(page); await choosePill(page);
    await page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" }).click();
    await expect(page.getByRole("heading", { name: outcome === "success" ? "Đột phá thành công" : "Đột phá thất bại", exact: true })).toBeVisible();
    await expect(page.getByRole("dialog")).toContainText("Tụ Khí Đan đã dùng1");
    const state = await (await request.get(`${backend}/game/state`)).json();
    expect(state.player.qi_gathering_pills).toBe(2);
    await page.evaluate(() => localStorage.clear());
    await page.close();
    const context = await browser.newContext();
    const reopened = await context.newPage(); await forward(reopened);
    await reopened.goto("http://127.0.0.1:3002/#inventory");
    await expect(reopened.getByRole("article", { name: "Tụ Khí Đan" })).toContainText("Số lượng: 2");
    await context.close();
  });
}

test("no pills still allows an unsupported breakthrough", async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/no-pills`);
  await openPreview(page);
  await expect(page.getByRole("checkbox")).toBeDisabled();
  await page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" }).click();
  await expect(page.getByRole("dialog")).toContainText("Tụ Khí Đan đã dùng0");
  expect((await (await request.get(`${backend}/game/state`)).json()).player.qi_gathering_pills).toBe(0);
});

test("late preview cannot overwrite the latest selection", async ({ page }) => {
  await openPreview(page);
  let release!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  let arrived!: () => void;
  const received = new Promise<void>(resolve => { arrived = resolve; });
  await page.route("**/api/breakthrough/preview?**", async route => {
    const url = new URL(route.request().url());
    const response = await route.fetch({ url: backend + "/breakthrough/preview" + url.search });
    arrived(); await gate; await route.fulfill({ response });
  });
  await page.getByRole("checkbox").check(); await received;
  await expect(page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" })).toBeDisabled();
  await page.getByRole("checkbox").uncheck();
  await expect(page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" })).toBeEnabled();
  const late = page.waitForResponse("**/api/breakthrough/preview?**"); release(); await late;
  await expect(page.getByRole("checkbox")).not.toBeChecked();
  await expect(page.getByRole("dialog")).toContainText("86,7%");
  await page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" }).click();
  await expect(page.getByRole("dialog")).toContainText("Tụ Khí Đan đã dùng0");
});

for (const failure of ["lost-reply", "server-error"]) {
  test(`${failure} retains payload through reload and replays one receipt`, async ({ page, request }) => {
    await openPreview(page); await choosePill(page);
    const payloads: unknown[] = [];
    await page.route("**/api/breakthrough/attempt", async route => {
      payloads.push(route.request().postDataJSON());
      const response = await route.fetch({ url: backend + "/breakthrough/attempt" });
      expect(response.ok()).toBe(true);
      if (payloads.length === 1) {
        if (failure === "lost-reply") await route.abort();
        else await route.fulfill({ status: 503, json: { detail: "unavailable" } });
      } else await route.fulfill({ response });
    });
    await page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" }).click();
    await expect(page.getByRole("alert").filter({ hasText: /\S/ })).toBeVisible();
    await page.reload();
    await page.getByRole("button", { name: "KIỂM TRA KẾT QUẢ" }).click();
    await expect(page.getByRole("heading", { name: "Đột phá thành công", exact: true })).toBeVisible();
    expect(payloads).toHaveLength(2); expect(payloads[0]).toEqual(payloads[1]);
    expect((await (await request.get(`${backend}/game/state`)).json()).player.qi_gathering_pills).toBe(2);
    expect(await page.evaluate(() => Object.keys(localStorage).filter(k => k.startsWith("breakthrough-pending:")))).toEqual([]);
  });
}

test("storage write failure stops before sending", async ({ page }) => {
  await openPreview(page); await choosePill(page);
  let sent = 0; page.on("request", req => { if (req.url().endsWith("/attempt")) sent++; });
  await page.evaluate(() => { Storage.prototype.setItem = () => { throw new Error("quota"); }; });
  await page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" }).click();
  await expect(page.getByRole("alert").filter({ hasText: /\S/ })).toContainText("Không thể lưu");
  expect(sent).toBe(0);
});

test("confirmed result survives state refresh failure and can sync again", async ({ page }) => {
  await openPreview(page); await choosePill(page);
  await page.route("**/api/game/state", route => route.abort());
  await page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" }).click();
  await expect(page.getByRole("heading", { name: "Đột phá thành công", exact: true })).toBeVisible();
  await expect(page.getByRole("alert").filter({ hasText: /\S/ })).toBeVisible();
  await page.unroute("**/api/game/state");
  await page.getByRole("button", { name: "Đồng bộ lại hành trình" }).click();
  await expect(page.getByRole("alert").filter({ hasText: /\S/ })).toHaveCount(0);
  await page.getByRole("button", { name: "TIẾP TỤC TIÊN LỘ" }).click();
  await page.goto("/#inventory");
  await expect(page.getByRole("article", { name: "Tụ Khí Đan" })).toContainText("Số lượng: 2");
});

test("conflicting id is rejected without additional consumption", async ({ page, request }) => {
  const state = await (await request.get(`${backend}/game/state`)).json();
  const preview = await (await request.get(`${backend}/breakthrough/preview`)).json();
  const payload = { request_id: crypto.randomUUID(), revision: preview.revision, item_key: null, quantity: 0 };
  expect((await request.post(`${backend}/breakthrough/attempt`, { data: payload })).ok()).toBe(true);
  await page.goto("/");
  await page.evaluate(({ id, payload }) => localStorage.setItem(`breakthrough-pending:${id}`, JSON.stringify({ ...payload, item_key: "items/qi_gathering_pill", quantity: 1 })), { id: state.player.id, payload });
  await page.reload();
  await page.getByRole("button", { name: "KIỂM TRA KẾT QUẢ" }).click();
  await expect(page.getByRole("alert").filter({ hasText: /\S/ })).toContainText("lựa chọn khác");
  expect((await (await request.get(`${backend}/game/state`)).json()).player.qi_gathering_pills).toBe(3);
});

test("foreign save pending is ignored; malformed current pending blocks a new attempt", async ({ page, request }) => {
  const state = await (await request.get(`${backend}/game/state`)).json();
  await page.goto("/");
  await page.evaluate(id => localStorage.setItem(`breakthrough-pending:${id + 100}`, "invalid"), state.player.id);
  await page.reload();
  await page.getByRole("button", { name: "ĐỘT PHÁ", exact: true }).click();
  await expect(page.getByRole("button", { name: "BẮT ĐẦU ĐỘT PHÁ" })).toBeEnabled();
  await page.keyboard.press("Escape");
  await page.evaluate(id => localStorage.setItem(`breakthrough-pending:${id}`, "{}"), state.player.id);
  await page.getByRole("button", { name: "ĐỘT PHÁ", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: /\S/ })).toContainText("không hợp lệ");
  await expect(page.getByRole("dialog")).toHaveCount(0);
});
