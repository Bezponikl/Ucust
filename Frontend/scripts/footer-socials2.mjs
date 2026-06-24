import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
await page.goto("http://localhost:3000", { waitUntil: "networkidle" });
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForTimeout(400);
const links = await page.locator("footer ul").first().locator("a").all();
for (let i = 0; i < links.length; i++) {
  await links[i].screenshot({ path: `screenshots/footer-social-${i}.png` });
  const src = await links[i].locator("img").getAttribute("src");
  console.log(i, src);
}
await browser.close();
