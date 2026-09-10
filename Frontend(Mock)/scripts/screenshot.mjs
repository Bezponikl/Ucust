import { chromium } from "playwright";
import fs from "node:fs";

const outDir = "screenshots";
fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch();

const viewports = {
  desktop: { width: 1440, height: 900 },
  mobile: { width: 390, height: 844 },
};

for (const [name, viewport] of Object.entries(viewports)) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const errors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  page.on("pageerror", (err) => errors.push(String(err)));

  await page.goto("http://localhost:3000", { waitUntil: "networkidle" });
  await page.waitForTimeout(800);

  // Scroll through the page to trigger whileInView reveals
  const height = await page.evaluate(() => document.body.scrollHeight);
  for (let y = 0; y < height; y += viewport.height / 2) {
    await page.evaluate((y) => window.scrollTo(0, y), y);
    await page.waitForTimeout(350);
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(500);

  await page.screenshot({
    path: `${outDir}/${name}-full.png`,
    fullPage: true,
  });

  // Section-by-section screenshots for the desktop viewport
  if (name === "desktop") {
    const sections = {
      hero: "section:nth-of-type(1)",
      "trust-strip": "#features ~ * , section:has(> ul)",
      features: "#features",
      channels: "#channels",
      "how-it-works": "#how-it-works",
      "product-showcase": "#product-showcase",
      pricing: "#pricing",
      faq: "#faq",
    };
    for (const [section, selector] of Object.entries(sections)) {
      try {
        const locator = page.locator(selector).first();
        await locator.scrollIntoViewIfNeeded();
        await page.waitForTimeout(400);
        await locator.screenshot({ path: `${outDir}/${name}-${section}.png` });
      } catch (e) {
        console.log(`skip ${section}:`, e.message.split("\n")[0]);
      }
    }
  }

  console.log(`${name}: console errors =`, errors);
  await context.close();
}

await browser.close();
