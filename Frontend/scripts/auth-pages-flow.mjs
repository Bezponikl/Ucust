import { chromium } from "playwright";

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
const errors = [];
page.on("console", (msg) => { if (msg.type() === "error") errors.push(msg.text()); });
page.on("pageerror", (err) => errors.push(err.message));

await page.goto("http://localhost:3000", { waitUntil: "networkidle" });
await page.getByRole("button", { name: "Зарегистрироваться" }).click();
await page.waitForURL("**/signup");
await page.screenshot({ path: "screenshots/flow-1-signup.png" });

await page.getByRole("textbox", { name: "Имя" }).fill("Иван");
await page.getByRole("textbox", { name: "Фамилия" }).fill("Иванов");
await page.getByRole("textbox", { name: "Email" }).fill("flow-demo@example.com");
await page.locator('input[type="password"]').nth(0).fill("password123");
await page.locator('input[type="password"]').nth(1).fill("password123");
await page.locator('input[type="checkbox"]').check();
await page.locator('form button[type="submit"]').click();
await page.waitForURL("**/signup/verify-email");
await page.screenshot({ path: "screenshots/flow-2-verify-email.png" });

await page.goto("http://localhost:3000/signup/confirm", { waitUntil: "networkidle" });
await page.screenshot({ path: "screenshots/flow-3-confirm.png" });
await page.locator("button", { hasText: "Продолжить" }).click();
await page.waitForURL("**/onboarding");
console.log("final url:", page.url());

await page.goto("http://localhost:3000/legal", { waitUntil: "networkidle" });
await page.screenshot({ path: "screenshots/flow-4-legal-hub.png" });
console.log("legal doc links:", await page.locator('a[href^="/legal/"]').count());

await page.goto("http://localhost:3000/login", { waitUntil: "networkidle" });
await page.screenshot({ path: "screenshots/flow-5-login.png" });

console.log("errors:", errors);
await browser.close();
