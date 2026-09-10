"use client";

import { motion, useReducedMotion } from "framer-motion";
import Icon from "./ui/Icon";
import ShaderLayer from "./ui/ShaderLayer";
import { useAuthModal } from "./AuthModalProvider";
import { fadeUp, staggerContainer } from "@/lib/motion";

const TRUST = ["Запуск за 2 минуты", "7 дней бесплатно", "Гарантия возврата"];

export default function Hero() {
  const { openSignup } = useAuthModal();
  const reduce = useReducedMotion();

  return (
    <section className="relative min-h-dvh overflow-hidden">
      {/* фон — живой WebGL mesh-шейдер (1в1 оригинал), пауза вне вьюпорта */}
      <ShaderLayer className="absolute inset-0" />

      {/* readability scrim */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-white/30 dark:bg-black/40"
      />

      <div className="relative z-10 mx-auto flex min-h-dvh max-w-(--container-page) flex-col items-center justify-center px-4 py-20 text-center sm:px-6">
        <motion.div
          variants={staggerContainer(0.12)}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center"
        >
          <motion.p
            variants={fadeUp}
            className="kicker mb-5 text-xs text-brand sm:text-sm"
          >
            ИИ-маркетолог для малого бизнеса
          </motion.p>

          <motion.h1
            variants={fadeUp}
            className="hero-title font-extrabold leading-[1.02] tracking-tight text-[2rem] sm:text-[3rem] lg:text-[3.75rem] xl:text-[4.375rem]"
          >
            Соцсети вашего бизнеса
            <br />
            ведёт <span className="whitespace-nowrap">ИИ&nbsp;— 24/7</span>
          </motion.h1>

          <motion.p
            variants={fadeUp}
            className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-[color:var(--hero-ink)] opacity-90 sm:text-lg"
          >
            Расскажите о бизнесе один раз — посты, публикацию и ответы на отзывы
            возьмёт на себя UCust.
          </motion.p>

          <motion.div
            variants={fadeUp}
            className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-center"
          >
            <button
              type="button"
              onClick={openSignup}
              className="btn-glass-blue inline-flex items-center justify-center px-6 py-3.5 text-sm font-semibold sm:text-base"
            >
              Попробовать бесплатно
            </button>
            <a
              href="#product-showcase"
              className="btn-glass inline-flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-medium ring-1 ring-inset ring-ink/15 dark:ring-white/30 sm:text-base"
            >
              Посмотреть продукт
              <Icon name="arrow-right" size={16} />
            </a>
          </motion.div>

          <motion.div
            variants={fadeUp}
            className="mt-7 inline-flex flex-col gap-2.5 rounded-2xl border border-white/60 bg-white/55 px-4 py-3 shadow-soft dark:border-white/15 dark:bg-white/10 sm:flex-row sm:items-center sm:gap-x-5 sm:gap-y-0 sm:px-5 sm:py-2.5"
          >
            {TRUST.map((t) => (
              <span
                key={t}
                className="flex items-center gap-1.5 whitespace-nowrap text-sm font-medium text-[color:var(--hero-ink)]"
              >
                <Icon name="check" size={14} className="shrink-0 text-brand" />
                {t}
              </span>
            ))}
          </motion.div>
        </motion.div>
      </div>

      {/* Ненавязчивая стрелка «ниже есть контент» */}
      <motion.a
        href="#how-it-works"
        aria-label="Листать вниз"
        className="absolute bottom-5 left-1/2 z-10 -translate-x-1/2 text-[color:var(--hero-ink)] opacity-35 transition-opacity hover:opacity-70 sm:bottom-6"
        animate={reduce ? undefined : { y: [0, 7, 0] }}
        transition={{ duration: 1.9, repeat: Infinity, ease: "easeInOut" }}
      >
        <Icon name="chevron-down" size={30} />
      </motion.a>
    </section>
  );
}
