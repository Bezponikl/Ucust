"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform, useReducedMotion } from "framer-motion";
import { LayoutDashboard, CalendarCheck, TrendingUp, Play } from "lucide-react";
import Reveal from "./Reveal";

const HIGHLIGHTS = [
  {
    icon: LayoutDashboard,
    text: "Единый дашборд для всех соцсетей и каналов.",
    gradient: "from-sky-400 to-blue-600",
  },
  {
    icon: CalendarCheck,
    text: "Контент-план на неделю вперёд — видно всё сразу.",
    gradient: "from-emerald-400 to-teal-500",
  },
  {
    icon: TrendingUp,
    text: "Понятная аналитика без лишних цифр.",
    gradient: "from-amber-300 to-orange-500",
  },
];

export default function ProductShowcase() {
  const ref = useRef<HTMLDivElement>(null);
  const prefersReducedMotion = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const rotate = useTransform(scrollYProgress, [0, 0.5, 1], [4, 0, -4]);
  const y = useTransform(scrollYProgress, [0, 0.5, 1], [24, 0, -24]);

  return (
    <section id="product-showcase">
      <div className="mx-auto max-w-(--container-page) px-5 py-16 sm:px-6 sm:py-24 lg:py-32">
        <Reveal>
          <h2 className="max-w-2xl text-3xl font-extrabold leading-tight tracking-tight text-ink sm:text-4xl">
            Посмотрите, как это выглядит внутри
          </h2>
        </Reveal>

        <Reveal delay={0.1} className="mt-12 rounded-3xl bg-card p-5 shadow-soft sm:mt-16 sm:p-8 lg:p-10">
          <div className="grid gap-10 lg:grid-cols-[1fr_320px] lg:items-center lg:gap-14">
            <motion.div
              ref={ref}
              style={
                prefersReducedMotion
                  ? undefined
                  : { rotate, y, transformPerspective: 1200 }
              }
              whileHover={prefersReducedMotion ? undefined : { scale: 1.015 }}
              transition={{ type: "spring", stiffness: 220, damping: 22 }}
              className="group relative flex aspect-[16/10] w-full items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-br from-surface-blue via-surface-soft to-surface-blue"
            >
              <div aria-hidden="true" className="pointer-events-none absolute inset-0">
                <div className="absolute -left-12 -top-12 h-40 w-40 rounded-full bg-brand/10 blur-2xl transition-transform duration-700 ease-out group-hover:scale-150" />
                <div className="absolute -bottom-14 -right-14 h-48 w-48 rounded-full bg-hero-via/10 blur-2xl transition-transform duration-700 ease-out group-hover:scale-125" />
              </div>

              <div className="relative flex flex-col items-center gap-3">
                <div className="relative flex h-16 w-16 items-center justify-center sm:h-20 sm:w-20">
                  {!prefersReducedMotion &&
                    [0, 1].map((i) => (
                      <motion.span
                        key={i}
                        className="absolute inset-0 rounded-full border border-brand/30"
                        animate={{ scale: [1, 1.6], opacity: [0.6, 0] }}
                        transition={{
                          duration: 2.4,
                          repeat: Infinity,
                          ease: "easeOut",
                          delay: i * 1.2,
                        }}
                      />
                    ))}
                  <span className="relative flex h-16 w-16 items-center justify-center rounded-full bg-brand text-white shadow-soft transition-transform duration-300 group-hover:scale-110 sm:h-20 sm:w-20">
                    <Play size={28} className="ml-1" fill="currentColor" aria-hidden="true" />
                  </span>
                </div>
                <span className="font-display text-sm uppercase tracking-wide text-ink-muted">
                  Видео скоро
                </span>
              </div>
            </motion.div>

            <ul className="flex flex-col gap-6">
              {HIGHLIGHTS.map(({ icon: Icon, text, gradient }) => (
                <li key={text} className="flex items-start gap-3">
                  <span className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br shadow-soft ${gradient}`}>
                    <Icon size={18} className="text-white" aria-hidden="true" />
                  </span>
                  <span className="pt-1.5 text-base leading-relaxed text-ink">
                    {text}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
