"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform, useReducedMotion } from "framer-motion";
import { LayoutDashboard, CalendarCheck, TrendingUp } from "lucide-react";
import Reveal from "./Reveal";
import ProductMockup from "./ProductMockup";

const HIGHLIGHTS = [
  {
    icon: LayoutDashboard,
    text: "Единый дашборд для всех соцсетей и каналов.",
  },
  {
    icon: CalendarCheck,
    text: "Контент-план на неделю вперёд — видно всё сразу.",
  },
  {
    icon: TrendingUp,
    text: "Понятная аналитика без лишних цифр.",
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
      <div className="mx-auto max-w-(--container-page) px-5 py-12 sm:px-6 sm:py-16 lg:py-20">
        <Reveal>
          <p className="kicker mb-4 text-xs text-brand sm:text-sm">Продукт</p>
          <h2 className="max-w-2xl text-3xl leading-tight tracking-tight text-ink sm:text-4xl">
            Посмотрите, как это выглядит внутри
          </h2>
        </Reveal>

        <Reveal delay={0.1} className="mt-12 rounded-[32px] bg-card p-5 shadow-soft sm:mt-16 sm:p-8 lg:p-10">
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
              className="group relative aspect-[4/5] w-full overflow-hidden rounded-[24px] bg-gradient-to-br from-surface-blue via-surface-soft to-surface-blue p-4 sm:aspect-[16/10] sm:p-6"
            >
              <div aria-hidden="true" className="pointer-events-none absolute inset-0">
                <div className="absolute -left-12 -top-12 h-40 w-40 rounded-full bg-brand/10 blur-2xl transition-transform duration-700 ease-out group-hover:scale-150" />
                <div className="absolute -bottom-14 -right-14 h-48 w-48 rounded-full bg-hero-via/10 blur-2xl transition-transform duration-700 ease-out group-hover:scale-125" />
              </div>

              <div className="relative h-full w-full">
                <ProductMockup />
              </div>
            </motion.div>

            <ul className="flex flex-col gap-6">
              {HIGHLIGHTS.map(({ icon: Icon, text }) => (
                <li key={text} className="flex items-start gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[14px] bg-brand-tint text-brand">
                    <Icon size={18} aria-hidden="true" />
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
