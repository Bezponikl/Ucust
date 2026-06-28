"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import HeroArt from "./HeroArt";
import { useAuthModal } from "./AuthModalProvider";
import { fadeUp, staggerContainer } from "@/lib/motion";

export default function Hero() {
  const { openSignup } = useAuthModal();

  return (
    <section className="relative overflow-hidden">
      {/* мягкое синее свечение на светлом фоне */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        <div className="absolute -right-32 -top-24 h-[560px] w-[560px] rounded-full bg-brand/10 blur-3xl" />
        <div className="absolute -left-24 top-44 h-[380px] w-[380px] rounded-full bg-surface-blue/40 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-(--container-page) px-4 pt-10 sm:px-6 sm:pt-14 lg:pt-20">
        <div className="grid items-center gap-6 lg:grid-cols-[1fr_1fr] lg:gap-8">
          <motion.div
            variants={staggerContainer(0.15)}
            initial="hidden"
            animate="visible"
          >
            <motion.p
              variants={fadeUp}
              className="kicker mb-5 text-xs text-brand sm:text-sm"
            >
              ИИ-маркетолог для малого бизнеса
            </motion.p>

            <motion.h1
              variants={fadeUp}
              className="text-[34px] font-extrabold leading-[1.08] tracking-tight text-ink-strong sm:text-[44px] lg:text-[56px] xl:text-[64px]"
            >
              Соцсети вашего бизнеса ведёт{" "}
              <span className="text-blue-glass">ИИ</span>
            </motion.h1>

            <motion.p
              variants={fadeUp}
              className="mt-5 max-w-xl text-base leading-relaxed text-ink-muted sm:text-lg"
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
                className="btn-glass-blue inline-flex items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold sm:text-base"
              >
                Попробовать бесплатно
              </button>
              <a
                href="#product-showcase"
                className="btn-glass inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3.5 text-sm font-medium sm:text-base"
              >
                Посмотреть демо
                <ArrowRight size={16} aria-hidden="true" />
              </a>
            </motion.div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="relative"
          >
            <div className="mx-auto aspect-square w-full max-w-[520px]">
              <HeroArt />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
