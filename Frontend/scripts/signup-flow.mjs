import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
const errors = [];
page.on("console", (msg) => { if (msg.type() === "error") errors.push(msg.text()); });
page.on("pageerror", (err) => errors.push(err.message));

await page.goto("http://localhost:3000", { waitUntil: "networkidle" });

const headerBtn = page.locator("header").getByRole("button", { name: "Зарегистрироваться" });
await headerBtn.click();
await page.waitForTimeout(400);
await page.screenshot({ path: "screenshots/signup-step1.png" });

await page.getByRole("textbox", { name: "Имя" }).fill("Иван");
await page.getByRole("textbox", { name: "Фамилия" }).fill("Иванов");
await page.getByRole("textbox", { name: /Отчество/ }).fill("Иванович");
await page.getByRole("textbox", { name: "Email" }).fill("test@example.com");
await page.locator('input[type="password"]').nth(0).fill("password123");
await page.locator('input[type="password"]').nth(1).fill("password123");
await page.locator('input[type="checkbox"]').check();
await page.waitForTimeout(200);
await page.screenshot({ path: "screenshots/signup-step1-filled.png" });

await page.locator('form button[type="submit"]').click();
await page.waitForTimeout(400);
await page.screenshot({ path: "screenshots/signup-step2-code.png" });

const codeInputs = page.locator('input[inputmode="numeric"]');
for (let i = 0; i < 6; i++) {
  await codeInputs.nth(i).type(String(i + 1));
}
await page.waitForTimeout(200);
await page.screenshot({ path: "screenshots/signup-step2-filled.png" });

console.log("errors:", errors);
await browser.close();
