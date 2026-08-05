"use client";

import { useCallback, useEffect, useState } from "react";
import { createPortal } from "react-dom";
import Icon from "@/components/ui/Icon";
import {
  TOUR_EVENT,
  TOUR_STEPS,
  getTourState,
  setTourState,
} from "@/lib/dashboard/tour";

interface Rect { top: number; left: number; width: number; height: number }

const CARD_W = 300;
const GAP = 12;
const EDGE = 12;

/** Первый ВИДИМЫЙ элемент с data-tour={id} (сайдбар на ПК, bottom-nav на мобиле). */
function findTarget(id: string): HTMLElement | null {
  const nodes = Array.from(document.querySelectorAll<HTMLElement>(`[data-tour="${id}"]`));
  return nodes.find((el) => el.offsetParent !== null && el.getBoundingClientRect().width > 0) ?? null;
}

function readRect(el: HTMLElement): Rect {
  const r = el.getBoundingClientRect();
  return { top: r.top, left: r.left, width: r.width, height: r.height };
}

/** Позиция карточки: сбоку, если помещается, иначе снизу/сверху по центру цели. */
function placeCard(rect: Rect, cardH: number) {
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  // Широкие цели (шапка, баннер во всю колонку) подписываем снизу — сбоку карточка
  // налезала бы на сайдбар и выглядела оторванной от элемента.
  const wideTarget = rect.width > vw * 0.4;
  const fitsRight = !wideTarget && rect.left + rect.width + GAP + CARD_W + EDGE <= vw;
  const fitsLeft = !wideTarget && rect.left - GAP - CARD_W - EDGE >= 0;
  const clamp = (v: number, min: number, max: number) => Math.min(Math.max(v, min), max);

  if (fitsRight || fitsLeft) {
    const left = fitsRight ? rect.left + rect.width + GAP : rect.left - GAP - CARD_W;
    const top = clamp(rect.top + rect.height / 2 - cardH / 2, EDGE, Math.max(EDGE, vh - cardH - EDGE));
    return { left, top };
  }

  const below = rect.top + rect.height + GAP;
  const top = below + cardH + EDGE <= vh ? below : Math.max(EDGE, rect.top - GAP - cardH);
  const left = clamp(rect.left + rect.width / 2 - CARD_W / 2, EDGE, Math.max(EDGE, vw - CARD_W - EDGE));
  return { left, top };
}

export default function TourGuide() {
  const [step, setStep] = useState<number | null>(null);
  const [rect, setRect] = useState<Rect | null>(null);
  const [cardH, setCardH] = useState(160);

  const finish = useCallback((state: "done" | "skipped") => {
    setStep(null);
    setRect(null);
    setTourState(state);
  }, []);

  // Автозапуск после онбординга (uc_tour=pending) + ручной запуск кнопкой «?».
  useEffect(() => {
    const begin = () => setStep(0);
    if (getTourState() === "pending") {
      const t = setTimeout(begin, 700); // ждём анимацию входа страницы
      return () => clearTimeout(t);
    }
    return undefined;
  }, []);

  useEffect(() => {
    const onStart = () => setStep(0);
    window.addEventListener(TOUR_EVENT, onStart);
    return () => window.removeEventListener(TOUR_EVENT, onStart);
  }, []);

  // Ищем цель текущего шага; если её нет на странице — перескакиваем дальше.
  useEffect(() => {
    if (step === null) return;
    const current = TOUR_STEPS[step];
    const el = current ? findTarget(current.target) : null;

    // Цели нет на этой странице (например, узкий экран) — переходим к следующей.
    // Через rAF, чтобы дать разметке домонтироваться и не дёргать state внутри эффекта.
    if (!el) {
      const skip = requestAnimationFrame(() => {
        if (step + 1 < TOUR_STEPS.length) setStep(step + 1);
        else finish("done");
      });
      return () => cancelAnimationFrame(skip);
    }

    el.scrollIntoView({ behavior: "smooth", block: "center" });
    const sync = () => setRect(readRect(el));
    const raf = requestAnimationFrame(sync);
    const settle = setTimeout(sync, 420); // после плавного скролла

    window.addEventListener("scroll", sync, true);
    window.addEventListener("resize", sync);
    return () => {
      cancelAnimationFrame(raf);
      clearTimeout(settle);
      window.removeEventListener("scroll", sync, true);
      window.removeEventListener("resize", sync);
    };
  }, [step, finish]);

  // Esc закрывает тур
  useEffect(() => {
    if (step === null) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") finish("skipped"); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [step, finish]);

  if (step === null || !rect || typeof document === "undefined") return null;

  const current = TOUR_STEPS[step];
  const last = step === TOUR_STEPS.length - 1;
  const pos = placeCard(rect, cardH);

  return createPortal(
    <>
      {/* Кольцо вокруг цели — интерфейс остаётся кликабельным */}
      <div
        aria-hidden="true"
        className="uc-tour-ring pointer-events-none fixed z-[95] rounded-2xl ring-2 ring-brand"
        style={{
          top: rect.top - 6,
          left: rect.left - 6,
          width: rect.width + 12,
          height: rect.height + 12,
        }}
      />

      <div
        role="dialog"
        aria-live="polite"
        aria-label={`Подсказка ${step + 1} из ${TOUR_STEPS.length}: ${current.title}`}
        ref={(el) => { if (el && el.offsetHeight !== cardH) setCardH(el.offsetHeight); }}
        className="uc-pop-in fixed z-[96] w-[300px] max-w-[calc(100vw-1.5rem)] rounded-2xl border border-border bg-card p-4 shadow-lift"
        style={{ top: pos.top, left: pos.left }}
      >
        <div className="mb-1.5 flex items-start justify-between gap-2">
          <span className="flex items-center gap-2 text-sm font-bold text-ink">
            <Icon name="sparkles" size={15} className="shrink-0 text-brand" aria-hidden="true" />
            {current.title}
          </span>
          <button
            type="button"
            onClick={() => finish("skipped")}
            aria-label="Закрыть подсказки"
            className="-mr-1 -mt-1 shrink-0 rounded-full p-1 text-ink-muted transition hover:bg-surface-soft hover:text-ink"
          >
            <Icon name="close" size={15} aria-hidden="true" />
          </button>
        </div>

        <p className="text-[0.8125rem] leading-relaxed text-ink-muted">{current.text}</p>

        <div className="mt-3.5 flex items-center justify-between gap-2">
          <span className="flex items-center gap-1.5" aria-hidden="true">
            {TOUR_STEPS.map((s, i) => (
              <span
                key={s.target}
                className={`h-1.5 rounded-full transition-all ${
                  i === step ? "w-4 bg-brand" : "w-1.5 bg-border"
                }`}
              />
            ))}
          </span>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => finish("skipped")}
              className="rounded-full px-3 py-1.5 text-xs font-medium text-ink-muted transition hover:text-ink"
            >
              Пропустить
            </button>
            <button
              type="button"
              onClick={() => (last ? finish("done") : setStep(step + 1))}
              className="btn-glass-blue inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold"
            >
              {last ? "Готово" : "Далее"}
              {!last && <Icon name="chevron-right" size={12} aria-hidden="true" />}
            </button>
          </div>
        </div>
      </div>
    </>,
    document.body,
  );
}
