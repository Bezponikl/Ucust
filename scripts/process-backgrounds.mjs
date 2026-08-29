// Пережимает пресеты фонов из C:\Users\Ант\OneDrive\Desktop\Фоны в public/backgrounds
// (единый формат/размер для быстрой загрузки как CSS background-image).
// Запуск: node scripts/process-backgrounds.mjs
import sharp from "sharp";
import path from "node:path";
import { mkdirSync } from "node:fs";

const SRC_DIR = "C:/Users/Ант/OneDrive/Desktop/Фоны";
const OUT_DIR = path.resolve("public/backgrounds");

const SOURCES = [
  { file: "autumn-forest-glows-with-vibrant-multi-colored-leaves-generated-by-ai.jpg", out: "bg-1.jpg" },
  { file: "autumn-forest-acrylic-painting-spooky-mystery-dusk-generated-by-ai.jpg", out: "bg-2.jpg" },
  { file: "futuristic-skyscraper-dominates-city-skyline-as-sun-sets-generated-by-ai.jpg", out: "bg-3.jpg" },
  { file: "mar-bustos-HsEz1XZ1TO8-unsplash.jpg", out: "bg-4.jpg" },
  { file: "Background 1.png", out: "bg-5.jpg" },
  { file: "Background 3.png", out: "bg-6.jpg" },
  { file: "Background 49.png", out: "bg-7.jpg" },
  { file: "Background 44.png", out: "bg-8.jpg" },
];

mkdirSync(OUT_DIR, { recursive: true });

for (const { file, out } of SOURCES) {
  const src = path.join(SRC_DIR, file);
  const dest = path.join(OUT_DIR, out);
  await sharp(src)
    .resize({ width: 1920, height: 1920, fit: "inside", withoutEnlargement: true })
    .jpeg({ quality: 78 })
    .toFile(dest);
  console.log(`OK: ${file} → public/backgrounds/${out}`);
}
