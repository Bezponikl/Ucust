"use client";

import { motion } from "framer-motion";
import { ArrowRight, Wallet, Timer, ShieldCheck } from "lucide-react";
import HeroVisual from "./HeroVisual";
import { useAuthModal } from "./AuthModalProvider";
import { fadeUp, staggerContainer } from "@/lib/motion";

const HIGHLIGHTS = [
  { icon: Wallet, label: "Без привязки карты" },
  { icon: Timer, label: "Первые посты за 5 минут" },
  { icon: ShieldCheck, label: "Данные хранятся в России" },
];

export default function Hero() {
  const { openSignup } = useAuthModal();

  return (
    <section className="relative">
      <div className="mx-auto max-w-(--container-page) px-4 pt-4 sm:px-6 sm:pt-6">
        <div className="relative overflow-hidden rounded-[28px] bg-gradient-to-br from-hero-from via-hero-via to-hero-to px-6 py-12 sm:rounded-[32px] sm:px-10 sm:py-16 lg:px-14 lg:py-20">
          {/* decorative chevrons */}
          <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
            <div className="absolute -right-32 -top-32 h-[460px] w-[460px] rotate-[18deg] rounded-[64px] bg-[var(--hero-chevron)] sm:h-[560px] sm:w-[560px]" />
            <div className="absolute -right-16 top-24 h-[340px] w-[340px] rotate-[18deg] rounded-[56px] bg-[var(--hero-chevron-soft)] sm:h-[420px] sm:w-[420px] sm:top-32" />
            <div className="absolute -bottom-28 left-1/3 h-[260px] w-[260px] rotate-[18deg] rounded-[48px] bg-[var(--hero-chevron-soft)] sm:h-[320px] sm:w-[320px]" />
          </div>

          <div className="relative grid items-center gap-12 lg:grid-cols-[52%_1fr] lg:gap-10">
            <motion.div
              variants={staggerContainer(0.15)}
              initial="hidden"
              animate="visible"
            >
              <motion.p
                variants={fadeUp}
                className="font-display mb-5 text-xs font-semibold uppercase tracking-[0.16em] text-white/70"
              >
                ИИ-маркетолог для малого бизнеса
              </motion.p>

              <motion.h1
                variants={fadeUp}
                className="text-[34px] font-extrabold leading-[1.08] tracking-tight text-white sm:text-[44px] lg:text-[56px] xl:text-[64px]"
              >
                Соцсети вашего бизнеса ведёт ИИ
              </motion.h1>

              <motion.p
                variants={fadeUp}
                className="mt-5 max-w-xl text-base leading-relaxed text-white/80 sm:text-lg"
              >
                Расскажите о бизнесе один раз — UCust сам напишет посты в вашем
                стиле и опубликует их в VK, Telegram, MAX и Одноклассниках по
                расписанию.
              </motion.p>

              <motion.div
                variants={fadeUp}
                className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center"
              >
                <button
                  type="button"
                  onClick={openSignup}
                  className="inline-flex items-center justify-center rounded-xl bg-white px-6 py-3.5 text-sm font-medium text-brand shadow-soft transition-all hover:-translate-y-0.5 hover:bg-white/90 sm:text-base"
                >
                  Попробовать бесплатно
                </button>
                <a
                  href="#product-showcase"
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/30 bg-transparent px-6 py-3.5 text-sm font-medium text-white transition-all hover:-translate-y-0.5 hover:border-white/60 sm:text-base"
                >
                  Посмотреть демо
                  <ArrowRight size={16} aria-hidden="true" />
                </a>
              </motion.div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.45, ease: [0.16, 1, 0.3, 1] }}
              className="flex justify-center lg:justify-end"
            >
              <HeroVisual />
            </motion.div>
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.55, ease: [0.16, 1, 0.3, 1] }}
          className="relative z-10 mx-3 -mt-8 rounded-2xl bg-card px-6 py-5 shadow-soft sm:mx-6 sm:-mt-10 sm:px-8 sm:py-6 lg:mx-10"
        >
          <ul className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
            {HIGHLIGHTS.map(({ icon: Icon, label }) => (
              <li key={label} className="flex items-center gap-3 text-sm font-medium text-ink sm:text-base">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-tint text-brand">
                  <Icon size={18} aria-hidden="true" />
                </span>
                {label}
              </li>
            ))}
          </ul>
        </motion.div>
      </div>
    </section>
  );
}
