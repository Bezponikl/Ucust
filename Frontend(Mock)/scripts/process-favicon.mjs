import sharp from "sharp";
import fs from "node:fs";
import path from "node:path";

const BRAND = path.resolve("public/brand");

// Кроп иконочного знака из тёмного логотипа (столбцы 0..362), затем trim до контента
async function makeIconSquare(size, padRatio = 0.08) {
  const cropped = await sharp(path.join(BRAND, "logo-darktext-4k.png"))
    .extract({ left: 0, top: 0, width: 362, height: 401 })
    .trim({ threshold: 1 })
    .png()
    .toBuffer();
  const m = await sharp(cropped).metadata();
  const inner = Math.round(size * (1 - padRatio * 2));
  const mark = await sharp(cropped)
    .resize({ width: inner, height: inner, fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .toBuffer();
  return sharp({ create: { width: size, height: size, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } } })
    .composite([{ input: mark, gravity: "center" }])
    .png()
    .toBuffer();
}

// Минимальный ICO-контейнер с PNG внутри (поддерживается всеми совр. браузерами/Windows)
function buildIco(pngs) {
  const count = pngs.length;
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0); // reserved
  header.writeUInt16LE(1, 2); // type: icon
  header.writeUInt16LE(count, 4);
  const entries = [];
  let offset = 6 + count * 16;
  for (const { size, data } of pngs) {
    const e = Buffer.alloc(16);
    e.writeUInt8(size >= 256 ? 0 : size, 0); // width
    e.writeUInt8(size >= 256 ? 0 : size, 1); // height
    e.writeUInt8(0, 2); // palette
    e.writeUInt8(0, 3); // reserved
    e.writeUInt16LE(1, 4); // color planes
    e.writeUInt16LE(32, 6); // bpp
    e.writeUInt32LE(data.length, 8);
    e.writeUInt32LE(offset, 12);
    entries.push(e);
    offset += data.length;
  }
  return Buffer.concat([header, ...entries, ...pngs.map((p) => p.data)]);
}

async function run() {
  // Переиспользуемый знак
  await fs.promises.writeFile(path.join(BRAND, "logo-icon.png"), await makeIconSquare(512));
  // app/icon.png — Next подхватит как favicon
  await fs.promises.writeFile(path.resolve("app/icon.png"), await makeIconSquare(512));
  // favicon.ico с PNG 16/32/48
  const sizes = [16, 32, 48];
  const pngs = [];
  for (const s of sizes) pngs.push({ size: s, data: await makeIconSquare(s, 0.04) });
  await fs.promises.writeFile(path.resolve("app/favicon.ico"), buildIco(pngs));
  console.log("favicon + icon.png written");
}

run().catch((e) => { console.error(e); process.exit(1); });
