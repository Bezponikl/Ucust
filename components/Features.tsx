"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Icon from "./ui/Icon";
import Reveal from "./Reveal";
import GradientScrollText from "./GradientScrollText";
import FeatureScene from "./features/FeatureScene";
import type { SceneId } from "./features/scenes.data";

type Feature = {
  id: SceneId;
  title: string;
  desc: string;
};

const FEATURES: Feature[] = [
  {
    id: "generation",
    title: "Генерация постов",
    desc: "Одна фраза — и готовый пост: текст, фото и хэштеги в вашем фирменном стиле.",
  },
  {
    id: "content-plan",
    title: "Контент-план",
    desc: "Календарь публикаций по всем каналам: видно, что и когда выходит.",
  },
  {
    id: "autopost",
    title: "Автопостинг",
    desc: "Публикует посты сам в заданное время, без ручной выгрузки.",
  },
  {
    id: "promo",
    title: "Акции и промо",
    desc: "Готовые кампании со скидками и спецпредложениями под ваш бизнес.",
  },
  {
    id: "reviews",
    title: "Отзывы",
    desc: "Собирает отзывы и предлагает готовый ответ клиенту — в вашем тоне.",
  },
  {
    id: "analytics",
    title: "Аналитика",
    desc: "Показывает, какие посты работают и что улучшить.",
  },
];

function FeatureCard({
  feature,
  index,
  active,
  pauseInactive,
}: {
  feature: Feature;
  index: number;
  active: boolean;
  pauseInactive: boolean;
}) {
  return (
    <article data-card data-index={index} className="w-full shrink-0 snap-start sm:w-[46%] lg:w-[31.5%]">
      <FeatureScene id={feature.id} active={active} pauseInactive={pauseInactive} />
      <h3 className="mt-5 text-xl font-bold text-ink sm:text-2xl">{feature.title}</h3>
      <p className="mt-2 max-w-sm text-base leading-relaxed text-ink-muted">
        {feature.desc}
      </p>
    </article>
  );
}

/* Пауза между автопрокрутками карусели. */
const AUTOPLAY_MS = 4000;

export default function Features() {
  const trackRef = useRef<HTMLDivElement>(null);
  const rafRef = useRef(0);
  const [canPrev, setCanPrev] = useState(false);
  const [canNext, setCanNext] = useState(true);
  const [page, setPage] = useState(0);
  // Автопрокрутка замирает, пока пользователь сам взаимодействует с каруселью:
  // курсор внутри, фокус с клавиатуры, палец на треке.
  const [held, setHeld] = useState(false);
  const [inView, setInView] = useState(false);
  // Мобилка (одна карточка на экране): пауза неактивных + рестарт при переключении.
  // Анимируем ТОЛЬКО реально видимые на экране карточки — остальные на паузе.
  // Иначе на десктопе крутятся все 6 сцен разом и это лагает. root = вьюпорт,
  // поэтому пауза срабатывает и при горизонтальном листании карусели, и когда
  // вся секция ушла из вида по вертикали.
  const [visible, setVisible] = useState<Set<number>>(() => new Set([0, 1, 2]));

  useEffect(() => {
    const el = trackRef.current;
    if (!el) return;
    const io = new IntersectionObserver(
      (entries) => {
        setVisible((prev) => {
          const next = new Set(prev);
          let changed = false;
          for (const e of entries) {
            const idx = Number((e.target as HTMLElement).dataset.index);
            if (Number.isNaN(idx)) continue;
            const vis = e.isIntersecting && e.intersectionRatio >= 0.5;
            if (vis && !next.has(idx)) {
              next.add(idx);
              changed = true;
            } else if (!vis && next.has(idx)) {
              next.delete(idx);
              changed = true;
            }
          }
          return changed ? next : prev;
        });
      },
      { threshold: [0, 0.5, 1] }
    );
    el.querySelectorAll("[data-card]").forEach((c) => io.observe(c));
    return () => io.disconnect();
  }, []);

  // Сама карусель едет только когда секция на экране — иначе это фоновая работа впустую.
  useEffect(() => {
    const el = trackRef.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => setInView(entry.isIntersecting),
      { threshold: 0.35 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  // Замеры лэйаута батчим в rAF: иначе каждый scroll-эвент во время плавной
  // прокрутки форсит reflow (это и давало подфриз на первом нажатии стрелки).
  const update = useCallback(() => {
    cancelAnimationFrame(rafRef.current);
    rafRef.current = requestAnimationFrame(() => {
      const el = trackRef.current;
      if (!el) return;
      setCanPrev(el.scrollLeft > 8);
      setCanNext(el.scrollLeft + el.clientWidth < el.scrollWidth - 8);
      const card = el.querySelector<HTMLElement>("[data-card]");
      const step = card ? card.offsetWidth + 20 : el.clientWidth * 0.8;
      setPage(step > 0 ? Math.round(el.scrollLeft / step) : 0);
    });
  }, []);

  useEffect(() => {
    update();
    const el = trackRef.current;
    if (!el) return;
    el.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      cancelAnimationFrame(rafRef.current);
      el.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, [update]);

  const scrollByCard = useCallback((dir: 1 | -1) => {
    const el = trackRef.current;
    if (!el) return;
    const card = el.querySelector<HTMLElement>("[data-card]");
    const step = card ? card.offsetWidth + 20 : el.clientWidth * 0.8;
    el.scrollBy({ left: dir * step, behavior: "smooth" });
  }, []);

  const scrollToCard = useCallback((i: number) => {
    const el = trackRef.current;
    if (!el) return;
    const card = el.querySelector<HTMLElement>("[data-card]");
    const step = card ? card.offsetWidth + 20 : el.clientWidth * 0.8;
    el.scrollTo({ left: i * step, behavior: "smooth" });
  }, []);

  // Автопрокрутка: раз в 4 с сдвигаем на карточку, с конца возвращаемся в начало.
  // prefers-reduced-motion читаем в эффекте, а не в рендере — иначе гидрация
  // разъезжается между сервером и клиентом.
  useEffect(() => {
    if (held || !inView) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const id = window.setInterval(() => {
      const el = trackRef.current;
      if (!el) return;
      const atEnd = el.scrollLeft + el.clientWidth >= el.scrollWidth - 8;
      if (atEnd) el.scrollTo({ left: 0, behavior: "smooth" });
      else scrollByCard(1);
    }, AUTOPLAY_MS);
    return () => window.clearInterval(id);
  }, [held, inView, scrollByCard]);

  const hold = () => setHeld(true);
  const release = () => setHeld(false);

  return (
    <section id="features">
      <div className="mx-auto max-w-(--container-page) px-5 py-12 sm:px-6 sm:py-16 lg:py-20">
        <Reveal>
          <p className="kicker mb-4 text-xs text-brand sm:text-sm">Возможности</p>
          <GradientScrollText
            as="h2"
            lines={["Всё, что нужно для", "соцсетей — в одном месте"]}
            className="max-w-2xl text-3xl font-bold leading-tight tracking-tight sm:text-4xl"
          />
        </Reveal>

        <div
          ref={trackRef}
          onMouseEnter={hold}
          onMouseLeave={release}
          onFocusCapture={hold}
          onBlurCapture={release}
          onPointerDown={hold}
          onPointerUp={release}
          onPointerCancel={release}
          className="no-scrollbar mt-10 flex snap-x snap-mandatory gap-5 overflow-x-auto pb-2 sm:mt-14"
        >
          {FEATURES.map((feature, i) => (
            <FeatureCard
              key={feature.id}
              feature={feature}
              index={i}
              active={visible.has(i)}
              pauseInactive
            />
          ))}
        </div>

        {/* Точки — основная навигация (работает и на тач-экранах), стрелки — вспомогательная. */}
        <div className="mt-7 flex items-center justify-between gap-4">
          <div className="flex flex-1 items-center justify-center gap-1 sm:justify-start sm:gap-2">
            {FEATURES.map((feature, i) => (
              <button
                key={feature.id}
                type="button"
                aria-label={`Показать: ${feature.title}`}
                aria-current={i === page}
                onClick={() => {
                  hold();
                  scrollToCard(i);
                }}
                className="group flex h-11 w-7 items-center justify-center"
              >
                <span
                  className={`block h-2 rounded-full transition-all duration-300 ${
                    i === page ? "w-6 bg-brand" : "w-2 bg-ink/25 group-hover:bg-ink/45"
                  }`}
                />
              </button>
            ))}
          </div>

          <div className="flex shrink-0 gap-3">
            <button
              type="button"
              aria-label="Предыдущие карточки"
              onClick={() => {
                hold();
                scrollByCard(-1);
              }}
              disabled={!canPrev}
              className="btn-glass flex h-12 w-12 items-center justify-center"
            >
              <Icon name="chevron-left" size={20} />
            </button>
            <button
              type="button"
              aria-label="Следующие карточки"
              onClick={() => {
                hold();
                scrollByCard(1);
              }}
              disabled={!canNext}
              className="btn-glass flex h-12 w-12 items-center justify-center"
            >
              <Icon name="chevron-right" size={20} />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
