import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
const errors = [];
page.on("console", (msg) => { if (msg.type() === "error") errors.push(msg.text()); });
await page.goto("http://localhost:3000", { waitUntil: "networkidle" });

// Hero CTA
await page.locator("section").first().getByRole("button", { name: "Попробовать бесплатно" }).click();
await page.waitForTimeout(300);
console.log("hero -> dialog visible:", await page.locator('[role="dialog"]').isVisible());
await page.keyboard.press("Escape");
await page.waitForTimeout(300);

// Pricing CTA (highlighted plan)
await page.locator("#pricing").scrollIntoViewIfNeeded();
await page.locator("#pricing").getByRole("button", { name: "Попробовать бесплатно" }).first().click();
await page.waitForTimeout(300);
console.log("pricing -> dialog visible:", await page.locator('[role="dialog"]').isVisible());
console.log("pricing -> title:", await page.locator("#signup-modal-title").textContent());
await page.keyboard.press("Escape");
await page.waitForTimeout(300);

console.log("errors:", errors);
await browser.close();
