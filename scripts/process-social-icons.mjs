import sharp from "sharp";
import path from "node:path";
import os from "node:os";

const PUBLIC = path.resolve("public");
const DESKTOP = path.join(os.homedir(), "OneDrive", "Desktop");

// Чистые официальные иконки VK/TG (прозрачные скруглённые края) → 128px, сохраняем альфу.
const JOBS = [
  { src: "Вк.png", out: "vk.png" },
  { src: "Телеграм.png", out: "telegram.png" },
];

for (const { src, out } of JOBS) {
  await sharp(path.join(DESKTOP, src))
    .ensureAlpha()
    .trim({ threshold: 1 })
    .resize(128, 128, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png({ compressionLevel: 9 })
    .toFile(path.join(PUBLIC, out));
  const m = await sharp(path.join(PUBLIC, out)).metadata();
  console.log(out, m.width + "x" + m.height);
}
console.log("done");
