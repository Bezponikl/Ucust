import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
await page.goto("http://localhost:3000", { waitUntil: "networkidle" });
await page.getByRole("button", { name: "Войти" }).click();
await page.waitForTimeout(500);

const dialog = page.locator('[role="dialog"]');
const box = await dialog.boundingBox();
console.log("dialog box:", JSON.stringify(box));

const overlay = page.locator('div.fixed.inset-0.z-\\[100\\]');
console.log("overlay count:", await overlay.count());
const overlayBox = await overlay.boundingBox();
console.log("overlay box:", JSON.stringify(overlayBox));

await dialog.screenshot({ path: "screenshots/auth-modal-dialog-only.png" });
await browser.close();
