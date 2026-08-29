"use client";

import { createElement, useEffect, useRef, type CSSProperties, type ElementType } from "react";

type Props = {
  /** Тег заголовка: h1 / h2 / span … */
  as?: ElementType;
  /** Строки заголовка (каждая заливается по мере прокрутки, строка за строкой). */
  lines: string[];
  className?: string;
  /** Для заголовков над первым экраном: сразу отрисовать залитым (без вспышки серого). */
  eager?: boolean;
};

/**
 * Флагманский заголовок: стартует приглушённым и заливается фирменным градиентом
 * по мере прокрутки (приём Apple, но нашим градиентом). Применять редко — 2–3 на страницу.
 * Стили в globals.css: .gsf-line. Уважает prefers-reduced-motion (сразу залит).
 */
export default function GradientScrollText({ as = "h2", lines, className, eager = false }: Props) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const el = ref.current;
    if (!el) return;
    const lineEls = Array.from(el.querySelectorAll<HTMLElement>(".gsf-line"));
    let raf = 0;

    const tick = () => {
      const vh = window.innerHeight;
      const start = vh * 0.85;
      const end = vh * 0.45;
      for (const l of lineEls) {
        const r = l.getBoundingClientRect();
        const p = Math.max(0, Math.min(1, (start - r.top) / (start - end)));
        l.style.setProperty("--p", p.toFixed(3));
      }
    };
    const onScroll = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(tick);
    };

    tick();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, [lines]);

  return createElement(
    as,
    { ref, className },
    lines.map((t, i) =>
      createElement(
        "span",
        {
          key: i,
          className: "gsf-line",
          "data-t": t,
          style: eager ? ({ "--p": 1 } as CSSProperties) : undefined,
        },
        t
      )
    )
  );
}
