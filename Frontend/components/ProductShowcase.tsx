"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform, useReducedMotion } from "framer-motion";
import Icon from "./ui/Icon";
import type { IconName } from "@/lib/icons/solar";
import Reveal from "./Reveal";
import SectionHeading from "./SectionHeading";
import ProductMockup from "./ProductMockup";

const HIGHLIGHTS: { icon: IconName; text: string }[] = [
  { icon: "dashboard", text: "Единый дашборд для всех соцсетей и каналов." },
  { icon: "calendar", text: "Контент-план на неделю вперёд — видно всё сразу." },
  { icon: "trending", text: "Понятная аналитика без лишних цифр." },
];

/* Вторичная плавающая карточка «сгенерированный пост» */
function PostCard() {
  return (
    <div className="w-[210px] rounded-[18px] border border-border bg-card p-3.5 shadow-lift">
      <div className="flex items-center gap-2">
        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand text-[0.6875rem] font-bold text-white">
          U
        </span>
        <div className="min-w-0">
          <div className="h-2 w-16 rounded-full bg-ink/15" />
          <div className="mt-1 h-2 w-10 rounded-full bg-ink/10" />
        </div>
        <span className="ml-auto inline-flex items-center gap-1 rounded-full bg-brand-tint px-2 py-0.5 text-[0.5625rem] font-semibold text-brand">
          <Icon name="sparkles-bold" size={9} /> ИИ
        </span>
      </div>
      <div className="mt-3 space-y-1.5">
        <div className="h-2 w-full rounded-full bg-ink/10" />
        <div className="h-2 w-[85%] rounded-full bg-ink/10" />
        <div className="h-2 w-[60%] rounded-full bg-ink/10" />
      </div>
      <div className="mt-3 h-16 w-full rounded-[12px] bg-gradient-to-br from-surface-blue via-surface-soft to-surface-blue" />
    </div>
  );
}

/* Вторичная плавающая карточка «охват» */
function ReachCard() {
  const bars = [40, 62, 48, 78, 90];
  return (
    <div className="w-[180px] rounded-[18px] border border-border bg-card p-3.5 shadow-lift">
      <div className="text-[0.625rem] text-ink-muted">Новых подписчиков</div>
      <div className="font-display text-gradient text-xl font-extrabold leading-tight">+342</div>
      <div className="text-[0.625rem] font-semibold text-success">за эту неделю</div>
      <div className="mt-2.5 flex h-10 items-end justify-between gap-1">
        {bars.map((h, i) => (
          <span
            key={i}
            className="w-full rounded-sm bg-brand/70"
            style={{ height: `${h}%` }}
          />
        ))}
      </div>
    </div>
  );
}

export default function ProductShowcase() {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  // Разная глубина параллакса → эффект «веера» устройств.
  const yMain = useTransform(scrollYProgress, [0, 1], [30, -30]);
  const rotMain = useTransform(scrollYProgress, [0, 0.5, 1], [3, 0, -3]);
  const yPost = useTransform(scrollYProgress, [0, 1], [70, -70]);
  const yReach = useTransform(scrollYProgress, [0, 1], [-60, 60]);

  return (
    <section id="product-showcase">
      <div className="mx-auto max-w-(--container-page) px-5 py-12 sm:px-6 sm:py-16 lg:py-20">
        <SectionHeading kicker="Продукт">
          Посмотрите, как это выглядит внутри
        </SectionHeading>

        <Reveal delay={0.1} className="mt-12 rounded-[32px] bg-card p-5 shadow-soft sm:mt-16 sm:p-8 lg:p-10">
          <div className="grid gap-10 lg:grid-cols-[1fr_320px] lg:items-center lg:gap-14">
            {/* device-cluster */}
            <div
              ref={ref}
              className="relative aspect-[4/5] w-full sm:aspect-[16/10]"
            >
              {/* фоновые блики */}
              <div aria-hidden="true" className="pointer-events-none absolute inset-0">
                <div className="absolute -left-12 -top-12 h-40 w-40 rounded-full bg-brand/10 blur-2xl" />
                <div className="absolute -bottom-14 -right-14 h-48 w-48 rounded-full bg-hero-via/10 blur-2xl" />
              </div>

              {/* центральный экран */}
              <motion.div
                style={
                  reduce
                    ? undefined
                    : { y: yMain, rotate: rotMain, transformPerspective: 1200 }
                }
                whileHover={reduce ? undefined : { scale: 1.015 }}
                transition={{ type: "spring", stiffness: 220, damping: 22 }}
                className="group relative z-10 h-full w-full overflow-hidden rounded-[24px] bg-gradient-to-br from-surface-blue via-surface-soft to-surface-blue p-4 shadow-lift sm:p-6"
              >
                <div className="relative h-full w-full">
                  <ProductMockup />
                </div>
              </motion.div>

              {/* вторичный экран: пост (справа сверху) */}
              <motion.div
                aria-hidden="true"
                style={reduce ? undefined : { y: yPost }}
                className="pointer-events-none absolute -right-4 -top-6 z-20 hidden rotate-[6deg] sm:block lg:-right-8"
              >
                <PostCard />
              </motion.div>

              {/* вторичный экран: охват (слева снизу) */}
              <motion.div
                aria-hidden="true"
                style={reduce ? undefined : { y: yReach }}
                className="pointer-events-none absolute -bottom-10 -left-6 z-20 hidden -rotate-[5deg] sm:block lg:-bottom-12 lg:-left-12"
              >
                <ReachCard />
              </motion.div>
            </div>

            <ul className="flex flex-col gap-6">
              {HIGHLIGHTS.map(({ icon, text }) => (
                <li key={text} className="flex items-start gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[14px] bg-brand-tint text-brand">
                    <Icon name={icon} size={18} aria-hidden="true" />
                  </span>
                  <span className="pt-1.5 text-base leading-relaxed text-ink">{text}</span>
                </li>
              ))}
            </ul>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
