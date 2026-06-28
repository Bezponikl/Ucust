"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import Reveal from "./Reveal";

type Feature = {
  id: string;
  title: string;
  desc: string;
  /** Путь к UI-экрану формата 4:5, напр. "/features/generation.webp".
   *  Пока файла нет — оставляем undefined, карточка показывает плейсхолдер.
   *  Как только экран готов: положить файл в public/features и вписать путь сюда. */
  image?: string;
  icon: React.ReactNode;
};

const ICON_PROPS = {
  width: 30,
  height: 30,
  viewBox: "0 0 24 24",
  fill: "none" as const,
  stroke: "currentColor",
  strokeWidth: 1.7,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
};

const FEATURES: Feature[] = [
  {
    id: "generation",
    title: "Генерация постов",
    desc: "Тексты и картинки по одному запросу — сразу в вашем фирменном стиле.",
    icon: (
      <svg {...ICON_PROPS} fill="currentColor" stroke="none">
        <path d="M12 2l1.6 4.4L18 8l-4.4 1.6L12 14l-1.6-4.4L6 8l4.4-1.6z" />
        <path d="M19 13l.8 2.2L22 16l-2.2.8L19 19l-.8-2.2L16 16l2.2-.8z" />
        <path d="M5 14l.7 1.8L7.5 16.5l-1.8.7L5 19l-.7-1.8L2.5 16.5l1.8-.7z" />
      </svg>
    ),
  },
  {
    id: "content-plan",
    title: "Контент-план",
    desc: "Календарь публикаций по всем каналам: видно, что и когда выходит.",
    icon: (
      <svg {...ICON_PROPS}>
        <rect x="3" y="4" width="18" height="17" rx="3" />
        <path d="M3 9h18M8 2v4M16 2v4" />
        <circle cx="8" cy="13" r="1.2" fill="currentColor" stroke="none" />
        <circle cx="12" cy="13" r="1.2" fill="currentColor" stroke="none" />
        <circle cx="16" cy="13" r="1.2" fill="currentColor" stroke="none" />
        <circle cx="8" cy="17" r="1.2" fill="currentColor" stroke="none" />
      </svg>
    ),
  },
  {
    id: "autopost",
    title: "Автопостинг",
    desc: "Публикует посты сам в заданное время, без ручной выгрузки.",
    icon: (
      <svg {...ICON_PROPS}>
        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4z" />
      </svg>
    ),
  },
  {
    id: "promo",
    title: "Акции и промо",
    desc: "Готовые кампании со скидками и спецпредложениями под ваш бизнес.",
    icon: (
      <svg {...ICON_PROPS}>
        <path d="M19 5L5 19" />
        <circle cx="6.5" cy="6.5" r="2.5" />
        <circle cx="17.5" cy="17.5" r="2.5" />
      </svg>
    ),
  },
  {
    id: "reviews",
    title: "Отзывы",
    desc: "Собирает отзывы и предлагает готовые ответы клиентам.",
    icon: (
      <svg {...ICON_PROPS}>
        <path
          d="M12 3.5l2.5 5.2 5.5.7-4 3.9 1 5.4L12 16.1 7.5 18.7l1-5.4-4-3.9 5.5-.7z"
          fill="currentColor"
          fillOpacity="0.15"
        />
      </svg>
    ),
  },
  {
    id: "chatbot",
    title: "Чат-бот",
    desc: "Отвечает на вопросы клиентов в ваших каналах круглосуточно.",
    icon: (
      <svg {...ICON_PROPS}>
        <path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 20l1.4-4.2A8.38 8.38 0 0 1 3.5 11.5 8.5 8.5 0 0 1 12 3a8.38 8.38 0 0 1 9 8.5z" />
        <circle cx="8.5" cy="11.5" r="1.1" fill="currentColor" stroke="none" />
        <circle cx="12" cy="11.5" r="1.1" fill="currentColor" stroke="none" />
        <circle cx="15.5" cy="11.5" r="1.1" fill="currentColor" stroke="none" />
      </svg>
    ),
  },
  {
    id: "analytics",
    title: "Аналитика",
    desc: "Показывает, какие посты работают и что улучшить.",
    icon: (
      <svg {...ICON_PROPS}>
        <path d="M3 3v18h18" />
        <rect x="6" y="13" width="2.6" height="6" rx="1" fill="currentColor" stroke="none" />
        <rect x="11" y="9" width="2.6" height="10" rx="1" fill="currentColor" stroke="none" />
        <rect x="16" y="11" width="2.6" height="8" rx="1" fill="currentColor" stroke="none" />
      </svg>
    ),
  },
];

function FeatureCard({ feature }: { feature: Feature }) {
  const [showImg, setShowImg] = useState(Boolean(feature.image));

  return (
    <article
      data-card
      className="w-[78%] shrink-0 snap-start sm:w-[46%] lg:w-[31.5%]"
    >
      <div className="group relative aspect-[4/5] overflow-hidden rounded-[28px] shadow-soft">
        {/* Плейсхолдер: фирменное голубое стекло + иконка функции */}
        <div className="panel-blue-glass absolute inset-0 flex items-center justify-center">
          <span className="flex h-20 w-20 items-center justify-center rounded-[22px] border border-white/70 bg-white/55 text-brand shadow-soft backdrop-blur-sm">
            {feature.icon}
          </span>
        </div>
        {/* UI-экран (когда появится файл); при ошибке загрузки откатываемся на плейсхолдер */}
        {showImg && feature.image && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={feature.image}
            alt={feature.title}
            onError={() => setShowImg(false)}
            className="absolute inset-0 z-10 h-full w-full object-cover transition-transform duration-500 ease-out group-hover:scale-[1.03]"
          />
        )}
      </div>
      <h3 className="mt-5 text-xl font-bold text-ink sm:text-2xl">{feature.title}</h3>
      <p className="mt-2 max-w-sm text-base leading-relaxed text-ink-muted">
        {feature.desc}
      </p>
    </article>
  );
}

export default function Features() {
  const trackRef = useRef<HTMLDivElement>(null);
  const [canPrev, setCanPrev] = useState(false);
  const [canNext, setCanNext] = useState(true);

  const update = useCallback(() => {
    const el = trackRef.current;
    if (!el) return;
    setCanPrev(el.scrollLeft > 8);
    setCanNext(el.scrollLeft + el.clientWidth < el.scrollWidth - 8);
  }, []);

  useEffect(() => {
    update();
    const el = trackRef.current;
    if (!el) return;
    el.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      el.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, [update]);

  const scrollByCard = (dir: 1 | -1) => {
    const el = trackRef.current;
    if (!el) return;
    const card = el.querySelector<HTMLElement>("[data-card]");
    const step = card ? card.offsetWidth + 20 : el.clientWidth * 0.8;
    el.scrollBy({ left: dir * step, behavior: "smooth" });
  };

  return (
    <section id="features">
      <div className="mx-auto max-w-(--container-page) px-5 py-12 sm:px-6 sm:py-16 lg:py-20">
        <Reveal>
          <p className="kicker mb-4 text-xs text-brand sm:text-sm">Возможности</p>
          <h2 className="max-w-2xl text-3xl leading-tight tracking-tight text-ink sm:text-4xl">
            Всё, что нужно для соцсетей, в одном месте
          </h2>
        </Reveal>

        <div
          ref={trackRef}
          className="no-scrollbar mt-10 flex snap-x snap-mandatory gap-5 overflow-x-auto pb-2 sm:mt-14"
        >
          {FEATURES.map((feature) => (
            <FeatureCard key={feature.id} feature={feature} />
          ))}
        </div>

        <div className="mt-7 flex justify-end gap-3">
          <button
            type="button"
            aria-label="Предыдущие карточки"
            onClick={() => scrollByCard(-1)}
            disabled={!canPrev}
            className="btn-glass flex h-12 w-12 items-center justify-center rounded-full"
          >
            <ChevronLeft size={20} aria-hidden="true" />
          </button>
          <button
            type="button"
            aria-label="Следующие карточки"
            onClick={() => scrollByCard(1)}
            disabled={!canNext}
            className="btn-glass flex h-12 w-12 items-center justify-center rounded-full"
          >
            <ChevronRight size={20} aria-hidden="true" />
          </button>
        </div>
      </div>
    </section>
  );
}
