"use client";

import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Check, Sparkles, SlidersHorizontal } from "lucide-react";
import Reveal from "./Reveal";
import { useAuthModal } from "./AuthModalProvider";
import TariffConfigurator from "./TariffConfigurator";
import { staggerContainer, fadeUp, viewportOnce } from "@/lib/motion";

const PLANS = [
  {
    name: "Старт",
    price: "1 500",
    tagline: "Чтобы попробовать.",
    features: [
      "До X генераций в месяц",
      "1 канал",
      "Контент-план",
      "Базовая аналитика",
    ],
    highlighted: false,
  },
  {
    name: "Бизнес",
    price: "3 500",
    tagline: "Для регулярного ведения.",
    features: [
      "До X генераций в месяц",
      "Все каналы",
      "Автопостинг",
      "Акции и промо",
      "Отзывы",
    ],
    highlighted: true,
  },
];

export default function Pricing() {
  const { openSignup } = useAuthModal();
  const reduce = useReducedMotion();
  const animate = !reduce;
  const [configOpen, setConfigOpen] = useState(false);

  return (
    <section id="pricing">
      <div className="mx-auto max-w-(--container-page) px-5 py-12 sm:px-6 sm:py-16 lg:py-20">
        <Reveal>
          <p className="kicker mb-4 text-xs text-brand sm:text-sm">Тарифы</p>
          <h2 className="max-w-2xl text-3xl leading-tight tracking-tight text-ink sm:text-4xl">
            Простые тарифы без сюрпризов
          </h2>
        </Reveal>

        <motion.div
          variants={staggerContainer(0.1)}
          initial="hidden"
          whileInView="visible"
          viewport={viewportOnce}
          className="mt-12 grid gap-6 sm:mt-16 lg:grid-cols-3"
        >
          {PLANS.map((plan) => (
            <motion.div
              key={plan.name}
              variants={fadeUp}
              className={`relative isolate flex flex-col rounded-[32px] p-7 sm:p-9 ${
                plan.highlighted
                  ? "bg-brand text-white shadow-lift lg:-translate-y-2"
                  : "bg-card shadow-soft"
              }`}
            >
              {plan.highlighted && (
                <>
                  <div
                    aria-hidden="true"
                    className="pointer-events-none absolute inset-0 -z-10 overflow-hidden rounded-[32px]"
                  >
                    <motion.span
                      className="absolute h-56 w-56 rounded-full bg-white/15 blur-2xl"
                      style={{ top: "-20%", left: "10%" }}
                      animate={
                        animate
                          ? { x: [0, 60, 0], y: [0, 40, 0], opacity: [0.5, 0.85, 0.5] }
                          : undefined
                      }
                      transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
                    />
                  </div>
                  <motion.span
                    className="absolute -top-3 left-7 inline-flex items-center gap-1 rounded-lg bg-white px-3 py-1 text-xs font-medium text-brand sm:left-8"
                    animate={animate ? { y: [0, -2, 0] } : undefined}
                    transition={{ duration: 2.6, repeat: Infinity, ease: "easeInOut" }}
                  >
                    <Sparkles size={12} aria-hidden="true" />
                    Популярный
                  </motion.span>
                </>
              )}

              <h3 className={`text-lg font-bold sm:text-xl ${plan.highlighted ? "text-white" : "text-ink"}`}>
                {plan.name}
              </h3>
              <p className={`mt-1 text-sm italic ${plan.highlighted ? "text-white/70" : "text-ink-muted"}`}>
                {plan.tagline}
              </p>

              <p className="mt-6 flex items-baseline gap-1.5">
                <span className={`font-display text-4xl font-extrabold tracking-tight sm:text-5xl ${plan.highlighted ? "text-white" : "text-ink"}`}>
                  {plan.price}
                </span>
                <span className={`font-display text-sm ${plan.highlighted ? "text-white/70" : "text-ink-muted"}`}>
                  ₽ / мес
                </span>
              </p>

              <ul className="mt-7 mb-8 flex flex-col gap-3">
                {plan.features.map((feature) => (
                  <li key={feature} className={`flex items-start gap-2.5 text-sm ${plan.highlighted ? "text-white" : "text-ink"}`}>
                    <Check size={18} className={`mt-0.5 shrink-0 ${plan.highlighted ? "text-white" : "text-brand"}`} aria-hidden="true" />
                    {feature}
                  </li>
                ))}
              </ul>

              <button
                type="button"
                onClick={openSignup}
                className={`mt-auto inline-flex items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold ${
                  plan.highlighted ? "btn-glass-dark" : "btn-glass"
                }`}
              >
                Попробовать бесплатно
              </button>
            </motion.div>
          ))}

          {/* Гибкий настраиваемый тариф */}
          <motion.div
            variants={fadeUp}
            className="relative isolate flex flex-col rounded-[32px] bg-card p-7 text-center shadow-soft sm:p-9"
          >
            <h3 className="flex items-center justify-center gap-2 text-lg font-bold text-ink sm:text-xl">
              <SlidersHorizontal size={20} className="text-brand" aria-hidden="true" />
              Свой тариф
            </h3>
            <p className="mt-1 text-sm text-ink-muted">Настройте под свои нужды</p>

            <p className="mt-6 flex items-baseline justify-center gap-1.5">
              <span className="text-base font-medium text-ink-muted">от</span>
              <span className="font-display text-4xl font-extrabold tracking-tight text-ink sm:text-5xl">
                1 500
              </span>
              <span className="font-display text-sm text-ink-muted">₽ / мес</span>
            </p>
            <p className="mt-1.5 text-sm text-ink-muted">Цена зависит от выбранных опций</p>

            <div className="my-7 flex flex-1 items-center justify-center">
              <span className="flex h-20 w-20 items-center justify-center rounded-full bg-brand-tint">
                <SlidersHorizontal size={32} className="text-brand" aria-hidden="true" />
              </span>
            </div>

            <p className="mb-7 text-sm leading-relaxed text-ink-muted">
              Выберите количество постов, проектов и дополнительные функции
            </p>

            <button
              type="button"
              onClick={() => setConfigOpen(true)}
              className="btn-glass-blue mt-auto inline-flex items-center justify-center rounded-xl px-6 py-3.5 text-sm font-semibold"
            >
              Настроить тариф
            </button>
          </motion.div>
        </motion.div>
      </div>

      <TariffConfigurator
        open={configOpen}
        onClose={() => setConfigOpen(false)}
        onStart={() => {
          setConfigOpen(false);
          openSignup();
        }}
      />
    </section>
  );
}
