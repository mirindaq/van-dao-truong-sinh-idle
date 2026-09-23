import { test, expect, type APIRequestContext } from "@playwright/test";

const backend = "http://127.0.0.1:8011";

test.beforeEach(async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/existing`);
  await page.route("**/api/**", async route => {
    const url = new URL(route.request().url());
    await route.fulfill({ response: await route.fetch({ url: backend + url.pathname.replace(/^\/api/, "") + url.search }) });
  });
});

async function raiseAffinity(request: APIRequestContext, npcKey: string, choiceKey: string) {
  const opened = await request.post(`${backend}/relationships/npcs/${npcKey}/prompt`);
  const profile = await opened.json();
  const response = await request.post(`${backend}/relationships/npcs/${npcKey}/interactions`, { data: {
    request_id: crypto.randomUUID(),
    prompt_key: profile.prompt.key,
    prompt_version: profile.prompt.version,
    choice_key: choiceKey,
  } });
  expect(response.ok()).toBeTruthy();
}

test("stacks two partners and dismisses only one share", async ({ page, request }) => {
  await raiseAffinity(request, "luo_qinghan", "together");
  await raiseAffinity(request, "xie_wuchen", "resolve");
  await page.goto("/#partner");
  await expect(page.getByRole("heading", { name: "Đạo Lữ" })).toBeVisible();

  const rate = page.getByText("Tốc độ tu vi", { exact: true }).locator("..").locator("strong");
  const plainRate = await rate.innerText();
  await page.getByRole("button", { name: "Kết duyên Lạc Thanh Hàn" }).click();
  await expect(page.getByText("Từ đạo lữ", { exact: true }).locator("..")).toContainText("+3");
  await expect.poll(() => rate.innerText()).not.toBe(plainRate);

  await page.getByRole("button", { name: "Kết duyên Tạ Vô Trần" }).click();
  await expect(page.getByText("Từ đạo lữ", { exact: true }).locator("..")).toContainText("+6");
  await expect(page.getByText("Đạo lữ đang kết", { exact: true }).locator("..")).toContainText("2");

  await page.getByRole("button", { name: "Gỡ duyên Lạc Thanh Hàn" }).click();
  await expect(page.getByText("Từ đạo lữ", { exact: true }).locator("..")).toContainText("+3");
  await expect(page.getByText("Đạo lữ đang kết", { exact: true }).locator("..")).toContainText("1");
  await page.reload();
  await expect(page.getByText("Từ đạo lữ", { exact: true }).locator("..")).toContainText("+3");
  await expect(page.getByText("Đạo lữ đang kết", { exact: true }).locator("..")).toContainText("1");
  for (const width of [1440, 390, 320]) {
    await page.setViewportSize({ width, height: 900 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page.getByText("Hệ số đạo lữ", { exact: true })).toBeVisible();
  }
  const dismiss = page.getByRole("button", { name: "Gỡ duyên Tạ Vô Trần" });
  await dismiss.focus();
  await dismiss.press("Enter");
  await expect(page.getByText("Đạo lữ đang kết", { exact: true }).locator("..")).toContainText("0");
  await page.goto("/#equipment");
  await expect(page.getByText("Từ đạo lữ", { exact: true }).locator("..")).toContainText("+0");
});

test("shows both alchemy recipes and crafts the six-herb batch", async ({ page, request }) => {
  await request.post(`${backend}/_test/prepare/herbs`);
  for (let index = 0; index < 3; index += 1) {
    const started = await request.post(`${backend}/exploration/run`, { data: { request_id: crypto.randomUUID(), location_key: "hau_son" } });
    const run = await started.json();
    await request.post(`${backend}/_test/clock`, { data: { at: new Date(new Date(run.exploration.available_at).getTime() + 1000).toISOString(), seed: 2 } });
    const finished = await request.get(`${backend}/exploration/run/${run.exploration.request_id}`);
    expect((await finished.json()).exploration.reward_item_quantity).toBe(1);
  }
  await page.goto("/#alchemy");
  await expect(page.getByRole("heading", { name: "Tụ Khí Đan", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Mẻ Tụ Khí Đan" })).toBeVisible();
  const pills = page.getByText("Tụ Khí Đan", { exact: true }).first().locator("..").locator("strong");
  const before = Number(await pills.innerText());
  await page.getByRole("button", { name: "Luyện Mẻ Tụ Khí Đan" }).click();
  await expect(page.getByText("Vân Linh Thảo", { exact: true }).first().locator("..")).toContainText("0");
  await expect(pills).toHaveText(String(before + 2));
});
