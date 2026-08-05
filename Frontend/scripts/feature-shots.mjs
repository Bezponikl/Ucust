import { chromium } from "playwright";
import fs from "node:fs";

const outDir = "public/features";
fs.mkdirSync(outDir, { recursive: true });

const BASE = "http://localhost:3111";

const shots = [
  { file: "generation", url: "/dashboard/create" },
  { file: "content-plan", url: "/dashboard/content" },
  { file: "autopost", url: "/dashboard/content", tab: "Месяц" },
  { file: "promo", url: "/dashboard/promos" },
  { file: "reviews", url: "/dashboard/reviews" },
  { file: "analytics", url: "/dashboard/analytics" },
];

const browser = await chromium.launch();

for (const theme of ["light", "dark"]) {
  const context = await browser.newContext({
    viewport: { width: 900, height: 1125 }, // портрет 4:5
    deviceScaleFactor: 2,
    colorScheme: theme,
  });
  const page = await context.newPage();
  const suffix = theme === "dark" ? "-dark" : "";

  for (const s of shots) {
    await page.goto(BASE + s.url, { waitUntil: "networkidle" });
    await page.waitForTimeout(1000);
    if (s.tab) {
      try {
        await page.getByRole("tab", { name: s.tab }).click();
        await page.waitForTimeout(600);
      } catch (e) {
        console.log("tab skip", s.file, e.message.split("\n")[0]);
      }
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(300);
    await page.screenshot({ path: `${outDir}/${s.file}${suffix}.jpg`, type: "jpeg", quality: 90 });
    console.log("saved", `${s.file}${suffix}`);
  }
  await context.close();
}

await browser.close();
console.log("done");
