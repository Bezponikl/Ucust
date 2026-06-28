// центры иконок каналов для «пингов» публикации (в % контейнера)
const PINGS = [
  { x: 78.4, y: 31.7, d: 0 },
  { x: 86.9, y: 43.7, d: 0.6 },
  { x: 88.1, y: 57.8, d: 1.2 },
  { x: 83.5, y: 73.7, d: 1.8 },
];

const SPHERE = { x: 42, y: 53 };

export default function HeroArt() {
  return (
    <div className="relative h-full w-full">
      {/* объединяющее синее гало */}
      <div
        aria-hidden="true"
        className="absolute inset-[8%] rounded-[42%] bg-[radial-gradient(circle,rgba(26,91,255,0.12),rgba(26,91,255,0)_70%)] blur-2xl"
      />

      {/* чистый рендер сцены (фон убран) */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/hero.webp?v=6"
        alt="ИИ собирает контент-план, генерирует посты с текстом и фото и публикует их во все соцсети"
        width={1040}
        height={1040}
        decoding="async"
        className="hero-art-img h-full w-full object-contain"
      />

      {/* живые акценты поверх */}
      <span className="hero-fx hero-fx-glow" style={{ left: `${SPHERE.x}%`, top: `${SPHERE.y}%` }} aria-hidden="true" />
      <span className="hero-fx hero-fx-ring" style={{ left: `${SPHERE.x}%`, top: `${SPHERE.y}%` }} aria-hidden="true" />
      {PINGS.map((p, i) => (
        <span
          key={i}
          className="hero-fx hero-fx-ping"
          style={{ left: `${p.x}%`, top: `${p.y}%`, animationDelay: `${p.d}s` }}
          aria-hidden="true"
        />
      ))}
    </div>
  );
}
