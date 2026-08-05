import { chromium } from "playwright";
import { pathToFileURL } from "node:url";
import fs from "node:fs";

fs.mkdirSync("screenshots/cards", { recursive: true });
const files = [
  ["card1", "C:\\Users\\Ант\\OneDrive\\Desktop\\UCust Card 1 - standalone.html"],
  ["card2", "C:\\Users\\Ант\\OneDrive\\Desktop\\UCust Card 2 - Контент-план.dc.html"],
  ["card3", "C:\\Users\\Ант\\OneDrive\\Desktop\\UCust Card 3 - Автопостинг.dc.html"],
];

const browser = await chromium.launch();
for (const [name, path] of files) {
  const ctx = await browser.newContext({ viewport: { width: 900, height: 1100 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e).slice(0, 200)));
  try {
    await page.goto(pathToFileURL(path).href, { waitUntil: "load", timeout: 20000 });
    await page.waitForTimeout(2500);
    await page.screenshot({ path: `screenshots/cards/${name}.png`, fullPage: false });
    // capture visible text for context
    const txt = await page.evaluate(() => document.body.innerText.replace(/\n{2,}/g, "\n").slice(0, 600));
    console.log(`\n=== ${name} === errors=${errors.length}`);
    console.log(txt);
  } catch (e) {
    console.log(`${name} FAILED:`, String(e).slice(0, 200), "errors:", errors);
  }
  await ctx.close();
}
await browser.close();
