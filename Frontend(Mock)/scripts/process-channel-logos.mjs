import sharp from "sharp";
import path from "node:path";
import os from "node:os";

const PUBLIC = path.resolve("public");
const DESKTOP = path.join(os.homedir(), "OneDrive", "Desktop");

// 1) RUTUBE — белая версия для тёмной темы (уже PNG с альфой), просто триммим
async function rutubeWhite() {
  const buf = await sharp(path.join(DESKTOP, "Logo_RUTUBE_white_color.png"))
    .ensureAlpha()
    .trim({ threshold: 1 })
    .png({ compressionLevel: 9 })
    .toBuffer();
  await sharp(buf).toFile(path.join(PUBLIC, "rutube-white.png"));
  const m = await sharp(buf).metadata();
  console.log("rutube-white:", m.width + "x" + m.height);
}

// 2) Avito — офиц. светлой версии нет. Перекрашиваем только чёрный текст в белый,
// цветные кружки (высокая насыщенность) оставляем как есть.
async function avitoWhite() {
  const { data, info } = await sharp(path.join(PUBLIC, "avito.png"))
    .ensureAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });
  const { width, height, channels } = info; // 4
  const out = Buffer.from(data);
  const CHROMA = 40; // ниже — считаем пиксель «серым» (текст/сглаживание)
  for (let i = 0; i < out.length; i += channels) {
    const r = out[i], g = out[i + 1], b = out[i + 2], a = out[i + 3];
    if (a === 0) continue;
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const chroma = max - min;
    // Серый и достаточно тёмный → это текст: красим в белый, альфу сохраняем.
    if (chroma < CHROMA && max < 160) {
      out[i] = 255;
      out[i + 1] = 255;
      out[i + 2] = 255;
    }
  }
  await sharp(out, { raw: { width, height, channels } })
    .png({ compressionLevel: 9 })
    .toFile(path.join(PUBLIC, "avito-white.png"));
  console.log("avito-white:", width + "x" + height);
}

await rutubeWhite();
await avitoWhite();
console.log("done");
