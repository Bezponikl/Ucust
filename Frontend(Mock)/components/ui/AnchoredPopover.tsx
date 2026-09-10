"use client";

import { useEffect, useLayoutEffect, useRef, useState, type ReactNode, type RefObject } from "react";
import { createPortal } from "react-dom";

const GAP = 6;
const EDGE = 8;

/**
 * Поповер, привязанный к элементу, но отрисованный в body.
 * Нужен там, где контейнер обрезает содержимое (модалка, панель с прокруткой):
 * позиция считается по координатам якоря и обновляется при скролле и ресайзе.
 */
export default function AnchoredPopover({
  anchorRef,
  open,
  onClose,
  width,
  align = "right",
  children,
  className = "",
  zIndex = 120,
}: {
  anchorRef: RefObject<HTMLElement | null>;
  open: boolean;
  onClose: () => void;
  /** Ширина поповера в пикселях — по ней считается выравнивание. */
  width: number;
  align?: "left" | "right";
  children: ReactNode;
  className?: string;
  zIndex?: number;
}) {
  const popRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ left: number; top: number } | null>(null);

  useLayoutEffect(() => {
    if (!open) return;

    const place = () => {
      const anchor = anchorRef.current;
      if (!anchor) return;
      const r = anchor.getBoundingClientRect();
      const h = popRef.current?.offsetHeight ?? 0;

      const rawLeft = align === "right" ? r.right - width : r.left;
      const left = Math.min(Math.max(EDGE, rawLeft), window.innerWidth - width - EDGE);

      const below = r.bottom + GAP;
      const fitsBelow = below + h <= window.innerHeight - EDGE;
      const top = fitsBelow ? below : Math.max(EDGE, r.top - GAP - h);

      setPos({ left, top });
    };

    place();
    // Скролл ловим на фазе перехвата: контейнер может быть любым внутри страницы
    window.addEventListener("scroll", place, true);
    window.addEventListener("resize", place);
    return () => {
      window.removeEventListener("scroll", place, true);
      window.removeEventListener("resize", place);
    };
  }, [open, align, width, anchorRef]);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      const t = e.target as Node;
      if (popRef.current?.contains(t) || anchorRef.current?.contains(t)) return;
      onClose();
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open, onClose, anchorRef]);

  // Открыть поповер можно только кликом, то есть уже после гидрации
  if (!open || typeof document === "undefined") return null;

  return createPortal(
    <div
      ref={popRef}
      style={{
        position: "fixed",
        left: pos?.left ?? -9999,
        top: pos?.top ?? -9999,
        width,
        zIndex,
        // До первого замера не показываем — иначе видно прыжок
        visibility: pos ? "visible" : "hidden",
      }}
      className={`uc-pop-in ${className}`}
    >
      {children}
    </div>,
    document.body,
  );
}
