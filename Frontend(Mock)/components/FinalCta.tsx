"use client";

import { motion, useReducedMotion } from "framer-motion";
import Icon from "./ui/Icon";
import { useAuthModal } from "./AuthModalProvider";
import { staggerContainer, fadeUp, viewportOnce } from "@/lib/motion";

/* Карточка реального сгенерированного поста — показываем продукт «в действии». */
function GeneratedPost() {
  return (
    <div className="w-full max-w-sm rounded-3xl border border-white/40 bg-card p-5 text-left shadow-lift">
      <div className="flex items-center gap-2.5">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand text-sm font-bold text-white">
          U
        </span>
        <div className="min-w-0 leading-tight">
          <p className="text-sm font-bold text-ink">Тёплый день</p>
          <p className="text-xs text-ink-muted">Кофейня · VK, Telegram</p>
        </div>
        <span className="ml-auto inline-flex items-center gap-1 rounded-full bg-brand-tint px-2.5 py-1 text-[0.625rem] font-semibold text-brand">
          <Icon name="sparkles-bold" size={10} /> ИИ
        </span>
      </div>

      <p className="mt-3.5 text-sm leading-relaxed text-ink">
        ☕ Осень — повод для нового ритуала. Раф с корицей до 12:00 — второй в
        подарок. Ждём в «Тёплом дне»!
      </p>
      <p className="mt-2 text-xs font-medium text-brand">#кофейня #раф #осень</p>

      <div className="mt-3.5 h-28 w-full rounded-2xl bg-gradient-to-br from-surface-blue via-surface-soft to-surface-blue" />

      <div className="mt-3.5 flex items-center gap-2 border-t border-border pt-3 text-xs text-ink-muted">
        <Icon name="calendar-check" size={14} className="text-brand" />
        Запланировано на завтра, 10:00
      </div>
    </div>
  );
}

export default function FinalCta() {
  const { openSignup } = useAuthModal();
  const reduce = useReducedMotion();

  return (
    <section className="pb-12 pt-4 sm:pb-16 sm:pt-6 lg:pb-20">
      <div className="mx-auto max-w-(--container-page) px-5 sm:px-6">
        <motion.div
          variants={staggerContainer(0.14)}
          initial="hidden"
          whileInView="visible"
          viewport={viewportOnce}
          className="relative overflow-hidden rounded-[28px] bg-gradient-to-br from-hero-from via-hero-via to-hero-to px-6 py-12 shadow-soft sm:rounded-[32px] sm:px-10 sm:py-16 lg:py-20"
        >
          {/* фоновые фигуры */}
          <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
            <div className="absolute -left-28 -top-28 h-[420px] w-[420px] rotate-[18deg] rounded-[72px] bg-[var(--hero-chevron)] sm:h-[480px] sm:w-[480px]" />
            <div className="absolute -bottom-28 -right-20 h-[320px] w-[320px] rounded-full bg-[var(--hero-chevron-soft)] blur-2xl" />
          </div>

          <div className="relative grid items-center gap-10 lg:grid-cols-2 lg:gap-12">
            {/* ── Текст ── */}
            <div className="text-center lg:text-left">
              <motion.h2
                variants={fadeUp}
                className="text-3xl font-extrabold leading-[1.1] tracking-tight text-white sm:text-4xl lg:text-5xl"
              >
                Маркетинг на автопилоте — начните сегодня
              </motion.h2>
              <motion.p
                variants={fadeUp}
                className="mx-auto mt-5 max-w-md text-base leading-relaxed text-white/85 sm:text-lg lg:mx-0"
              >
                Расскажите о бизнесе один раз — первый пост будет готов через 5
                минут.
              </motion.p>

              <motion.div variants={fadeUp}>
                <motion.button
                  type="button"
                  onClick={openSignup}
                  whileHover={reduce ? undefined : { scale: 1.04 }}
                  whileTap={reduce ? undefined : { scale: 0.97 }}
                  transition={{ type: "spring", stiffness: 400, damping: 22 }}
                  className="btn-glass-dark mt-8 inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold"
                >
                  Попробовать бесплатно
                  <Icon name="arrow-right" size={18} />
                </motion.button>
              </motion.div>

              <motion.p variants={fadeUp} className="mt-4 text-sm text-white/70">
                7 дней бесплатно · Без привязки карты · Гарантия возврата
              </motion.p>
            </div>

            {/* ── Пример поста ── */}
            <motion.div
              variants={fadeUp}
              className="flex justify-center lg:justify-end"
            >
              <GeneratedPost />
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
