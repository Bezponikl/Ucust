/** Что сейчас на проде: доступен ли дашборд и куда уходят запросы API. */
import { chromium } from "playwright";
const b = await chromium.launch();
const c = await b.newContext({ viewport:{width:1440,height:900} });
const pg = await c.newPage();
const api=[]; pg.on("request", r=>{ if(r.url().includes("/api/v0/")) api.push(r.url()); });
await pg.goto("https://ucust.online/dashboard", { waitUntil:"domcontentloaded", timeout:60000 });
await pg.waitForTimeout(3000);
console.log("ПРОД /dashboard →", pg.url());
console.log("запросы API:", [...new Set(api)].slice(0,5).join("\n  ") || "нет");
await pg.screenshot({ path:"screenshots/review/prod-before.png" });
await b.close();
