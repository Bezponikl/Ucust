import sharp from "sharp";
import path from "node:path";

const BRAND = path.resolve("public/brand");

// Убираем белый фон у JPG: альфа по «удалённости от белого» с мягким рампом,
// + unpremultiply над белым, чтобы у краёв тёмного текста не было серого ореола.
async function keyWhiteToAlpha(src) {
  const { data, info } = await sharp(src).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  const { width, height, channels } = info; // channels = 4
  const out = Buffer.alloc(data.length);
  const LO = 12;  // dist <= LO  -> полностью прозрачно (фон)
  const HI = 65;  // dist >= HI  -> полностью непрозрачно
  for (let i = 0; i < data.length; i += channels) {
    const r = data[i], g = data[i + 1], b = data[i + 2];
    const dist = Math.max(255 - r, 255 - g, 255 - b); // 0 = чистый белый
    let a = (dist - LO) / (HI - LO);
    a = a < 0 ? 0 : a > 1 ? 1 : a;
    if (a <= 0) {
      out[i] = out[i + 1] = out[i + 2] = 255;
      out[i + 3] = 0;
    } else if (a >= 1) {
      out[i] = r; out[i + 1] = g; out[i + 2] = b; out[i + 3] = 255;
    } else {
      // unpremultiply над белым: c_true = 255 + (c - 255) / a
      out[i]     = clamp(255 + (r - 255) / a);
      out[i + 1] = clamp(255 + (g - 255) / a);
      out[i + 2] = clamp(255 + (b - 255) / a);
      out[i + 3] = Math.round(a * 255);
    }
  }
  return sharp(out, { raw: { width, height, channels: 4 } });
}

const clamp = (v) => (v < 0 ? 0 : v > 255 ? 255 : Math.round(v));

async function run() {
  // 1) Тёмный логотип (для светлой темы) — из JPG, вырезаем белый фон
  const dark = (await keyWhiteToAlpha(path.join(BRAND, "_src-darktext.jpg")))
    .trim({ threshold: 1 });
  const darkBuf = await dark.png().toBuffer(); // зафиксировать trim
  const darkMeta = await sharp(darkBuf).metadata();
  console.log("darktext trimmed:", darkMeta.width + "x" + darkMeta.height);

  // Витрина для навбара/футера — webp по ширине 700 (как было)
  await sharp(darkBuf).resize({ width: 700 }).webp({ quality: 92 })
    .toFile("public/logo-wordmark.webp");
  // Hi-res архив бренда
  await sharp(darkBuf).png({ compressionLevel: 9 })
    .toFile(path.join(BRAND, "logo-darktext-4k.png"));

  // 2) Светлый логотип (для тёмной темы) — PNG уже с альфой
  const light = sharp(path.join(BRAND, "_src-lighttext.png")).trim({ threshold: 1 });
  const lightBuf = await light.png().toBuffer();
  const lightMeta = await sharp(lightBuf).metadata();
  console.log("lighttext trimmed:", lightMeta.width + "x" + lightMeta.height);

  await sharp(lightBuf).resize({ width: 700 }).webp({ quality: 92 })
    .toFile(path.join(BRAND, "logo-lighttext.webp"));
  await sharp(lightBuf).png({ compressionLevel: 9 })
    .toFile(path.join(BRAND, "logo-lighttext-4k.png"));

  console.log("done");
}

run().catch((e) => { console.error(e); process.exit(1); });
