"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  Sparkles,
  Send,
  CalendarDays,
  BarChart3,
  MessageCircle,
  ImageIcon,
} from "lucide-react";

const TILES: {
  icon: typeof Sparkles;
  gradient: string;
  className: string;
  duration: number;
  delay: number;
}[] = [
  {
    icon: Sparkles,
    gradient: "from-violet-400 to-purple-600",
    className: "left-2 top-2 sm:left-0 sm:top-4",
    duration: 5,
    delay: 0,
  },
  {
    icon: Send,
    gradient: "from-sky-400 to-blue-600",
    className: "right-0 top-10 sm:-right-3 sm:top-12",
    duration: 6,
    delay: 0.4,
  },
  {
    icon: CalendarDays,
    gradient: "from-emerald-400 to-teal-500",
    className: "-left-3 bottom-24 sm:-left-6",
    duration: 5.5,
    delay: 0.8,
  },
  {
    icon: BarChart3,
    gradient: "from-amber-300 to-orange-500",
    className: "right-2 bottom-8 sm:right-2",
    duration: 6.5,
    delay: 0.2,
  },
  {
    icon: MessageCircle,
    gradient: "from-pink-400 to-rose-500",
    className: "left-1/2 -top-4 -translate-x-1/2 sm:left-1/3",
    duration: 5,
    delay: 1.1,
  },
];

export default function HeroVisual() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <div className="relative h-[380px] w-full max-w-md sm:h-[440px]">
      {/* central content card */}
      <div className="absolute inset-x-6 top-10 rounded-2xl bg-card p-5 shadow-soft sm:inset-x-10 sm:p-6">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-tint font-display text-sm font-bold text-brand">
            П
          </span>
          <span className="text-sm font-medium text-ink">Кофейня «Пар»</span>
        </div>

        <p className="mt-3 text-sm leading-relaxed text-ink">
          Каждый вторник — любимый раф со скидкой 20% ☕️ Заходите согреться и
          зарядиться энергией!
        </p>

        <div className="mt-3 flex aspect-[16/10] w-full items-center justify-center rounded-xl border border-dashed border-border bg-surface-soft text-ink-muted">
          <ImageIcon size={22} aria-hidden="true" />
        </div>

        <div className="font-display mt-3 flex flex-wrap gap-x-2 gap-y-1 text-xs text-brand">
          <span>#кофейняпар</span>
          <span>#раф</span>
          <span>#акциядня</span>
        </div>
      </div>

      {/* floating Apple-style icon tiles */}
      {TILES.map(({ icon: Icon, gradient, className, duration, delay }, i) => (
        <motion.div
          key={i}
          className={`absolute flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br shadow-soft sm:h-16 sm:w-16 ${gradient} ${className}`}
          animate={
            prefersReducedMotion
              ? undefined
              : { y: [0, -10, 0] }
          }
          transition={{
            duration,
            delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <Icon size={26} className="text-white" aria-hidden="true" />
        </motion.div>
      ))}
    </div>
  );
}
