import { chromium } from "playwright";
const browser = await chromium.launch();

const consoleErrors = [];
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
page.on("console", (msg) => { if (msg.type() === "error") consoleErrors.push(msg.text()); });
await page.goto("http://localhost:3000", { waitUntil: "networkidle" });
await page.getByRole("button", { name: "Войти" }).click();
await page.waitForTimeout(400);
await page.screenshot({ path: "screenshots/auth-modal-desktop.png" });
console.log("desktop errors:", consoleErrors);

const ctxM = await browser.newContext({ viewport: { width: 390, height: 844 } });
const pageM = await ctxM.newPage();
const consoleErrorsM = [];
pageM.on("console", (msg) => { if (msg.type() === "error") consoleErrorsM.push(msg.text()); });
await pageM.goto("http://localhost:3000", { waitUntil: "networkidle" });
await pageM.getByRole("button", { name: open => true, exact: false }).first();
await pageM.getByLabel("Открыть меню").click();
await pageM.waitForTimeout(300);
await pageM.getByRole("button", { name: "Войти" }).click();
await pageM.waitForTimeout(400);
await pageM.screenshot({ path: "screenshots/auth-modal-mobile.png" });
console.log("mobile errors:", consoleErrorsM);

await browser.close();
