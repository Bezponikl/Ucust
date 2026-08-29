"use client";

import { useLayoutEffect, useState, type RefObject } from "react";

const EDGE = 12;

/**
 * Куда раскрывать выпадающий список: вниз (по умолчанию) или вверх, если снизу
 * не хватает места. Меряем по якорю — самому полю или кнопке, а не по панели,
 * поэтому высоту панели передаём оценкой.
 *
 * Возвращает "down" | "up". Пока закрыто — всегда "down", чтобы разметка на
 * сервере и на клиенте совпадала.
 */
export function useDropDirection(
  open: boolean,
  anchorRef: RefObject<HTMLElement | null>,
  panelHeight = 260,
): "down" | "up" {
  const [dir, setDir] = useState<"down" | "up">("down");

  useLayoutEffect(() => {
    if (!open) return;
    const measure = () => {
      const el = anchorRef.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      const below = window.innerHeight - r.bottom - EDGE;
      const above = r.top - EDGE;
      // Вверх уходим только если снизу не влезает, а сверху места больше.
      setDir(below < panelHeight && above > below ? "up" : "down");
    };
    measure();
    // Скролл ловим на фазе перехвата: якорь может лежать внутри своей прокрутки.
    window.addEventListener("scroll", measure, true);
    window.addEventListener("resize", measure);
    return () => {
      window.removeEventListener("scroll", measure, true);
      window.removeEventListener("resize", measure);
    };
  }, [open, anchorRef, panelHeight]);

  // Пока закрыто — всегда "down": так разметка совпадает на сервере и клиенте,
  // а сбрасывать состояние в эффекте (лишний каскад рендеров) не приходится.
  return open ? dir : "down";
}

/** Позиционные классы панели под выбранное направление. */
export function dropClass(dir: "down" | "up"): string {
  return dir === "up" ? "bottom-full mb-2" : "top-full mt-2";
}

/** То же, но для панелей с более плотным отступом (mt-1.5 в исходной вёрстке). */
export function dropClassTight(dir: "down" | "up"): string {
  return dir === "up" ? "bottom-full mb-1.5" : "top-full mt-1.5";
}
