import sharp from "sharp";

// Нормализуем новый арт под единый кадр step-картинок:
// холст 1600x1000, контент по горизонтали по центру, нижняя линия на y=949 (50px снизу).
const CANVAS_W = 1600, CANVAS_H = 1000;
const BOTTOM_PAD = 50;          // как у остальных шагов
const MAX_W = 1500, MAX_H = 900; // рамка для контента

const SRC = "public/brand/_src-step2.png";

async function run() {
  // 1) обрезать до непрозрачного контента
  const trimmed = await sharp(SRC).trim({ threshold: 1 }).png().toBuffer();
  const tm = await sharp(trimmed).metadata();
  console.log("trimmed:", tm.width + "x" + tm.height);

  // 2) вписать в рамку MAX_W x MAX_H с сохранением пропорций
  const fitted = await sharp(trimmed)
    .resize({ width: MAX_W, height: MAX_H, fit: "inside", withoutEnlargement: false })
    .png()
    .toBuffer();
  const fm = await sharp(fitted).metadata();

  // 3) положение: центр по X, нижняя линия на (CANVAS_H - 1 - BOTTOM_PAD)
  const left = Math.round((CANVAS_W - fm.width) / 2);
  const top = CANVAS_H - BOTTOM_PAD - fm.height;
  console.log("placed:", fm.width + "x" + fm.height, "left", left, "top", top);

  const canvas = sharp({
    create: { width: CANVAS_W, height: CANVAS_H, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } },
  }).composite([{ input: fitted, left, top: Math.max(0, top) }]);

  await canvas.webp({ quality: 90 }).toFile("public/step2.webp");
  console.log("written public/step2.webp");
}

run().catch((e) => { console.error(e); process.exit(1); });
