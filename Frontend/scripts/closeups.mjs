import { chromium } from "playwright";

const browser = await chromium.launch();
const ctxD = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const pageD = await ctxD.newPage();
await pageD.goto("http://localhost:3000", { waitUntil: "networkidle" });
await pageD.waitForTimeout(800);

for (const sel of ["#how-it-works", "#product-showcase", "#pricing", "#faq"]) {
  const loc = pageD.locator(sel).first();
  await loc.scrollIntoViewIfNeeded();
  await pageD.waitForTimeout(400);
  await loc.screenshot({ path: `screenshots/v2-${sel.replace("#", "")}.png` });
}

await pageD.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await pageD.waitForTimeout(400);
await pageD.screenshot({ path: "screenshots/v2-final.png" });

await browser.close();
