"use client";

import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import dynamic from "next/dynamic";
import { useIsDark } from "@/lib/useIsDark";

// WebGL-библиотека шейдера грузится динамически (ssr:false — без hydration mismatch).
const MeshGradient = dynamic(
  () => import("@paper-design/shaders-react").then((m) => m.MeshGradient),
  { ssr: false }
);

// Brand palette: blue → purple → pink → orange
const DARK_COLORS = ["#0a0b14", "#4f7dff", "#7b5cff", "#ff5fa2", "#ff8c4b"];
const LIGHT_COLORS = ["#eaf0ff", "#4f7dff", "#7b5cff", "#ff5fa2", "#ff8c4b"];

// Потолок разрешения канваса: mesh-градиент низкочастотный, супер-сэмплинг на
// retina не нужен — ограничиваем число фрагментов, чтобы на мобильных GPU не
// рендерить по 2–3 млн пикселей каждый кадр.
const MAX_PIXEL_COUNT = 1_100_000; // ≈ 1480×740

function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduced(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);
  return reduced;
}

// Пока hero виден — анимируем; ушёл из вьюпорта → speed=0 (либа полностью
// останавливает rAF, не стоит ни кадра CPU/GPU).
function useInView(ref: React.RefObject<HTMLElement | null>): boolean {
  const [inView, setInView] = useState(true);
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    const io = new IntersectionObserver(
      ([entry]) => setInView(entry.isIntersecting),
      { rootMargin: "0px", threshold: 0 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [ref]);
  return inView;
}

export function ShaderBackground({ children }: { children?: ReactNode }) {
  const isDark = useIsDark();
  const reduced = useReducedMotion();
  const colors = isDark ? DARK_COLORS : LIGHT_COLORS;

  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref);

  return (
    <div ref={ref} className="relative h-full w-full overflow-hidden">
      {reduced ? (
        <div
          aria-hidden
          className="absolute inset-0 h-full w-full"
          style={{
            background: `radial-gradient(120% 120% at 30% 20%, ${colors[1]}, ${colors[2]} 40%, ${colors[0]} 100%)`,
          }}
        />
      ) : (
        <MeshGradient
          className="absolute inset-0 h-full w-full"
          colors={colors}
          speed={inView ? 0.3 : 0}
          maxPixelCount={MAX_PIXEL_COUNT}
          minPixelRatio={1}
        />
      )}
      {children}
    </div>
  );
}
