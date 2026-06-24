"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";
import Reveal from "./Reveal";
import { useAuthModal } from "./AuthModalProvider";
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
  {
    name: "Профи",
    price: "7 500",
    tagline: "Для активного продвижения.",
    features: [
      "До X генераций в месяц",
      "Чат-бот",
      "Расширенная аналитика",
      "Командный доступ",
      "Приоритетная поддержка",
    ],
    highlighted: false,
  },
];

export default function Pricing() {
  const { openSignup } = useAuthModal();

  return (
    <section id="pricing">
      <div className="mx-auto max-w-(--container-page) px-5 py-16 sm:px-6 sm:py-24 lg:py-32">
        <Reveal>
          <h2 className="max-w-2xl text-3xl font-extrabold leading-tight tracking-tight text-ink sm:text-4xl">
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
              className={`relative flex flex-col rounded-2xl p-7 sm:p-8 ${
                plan.highlighted
                  ? "bg-brand text-white shadow-soft lg:-translate-y-2"
                  : "bg-card shadow-soft"
              }`}
            >
              {plan.highlighted && (
                <span className="absolute -top-3 left-7 rounded-lg bg-white px-3 py-1 text-xs font-medium text-brand sm:left-8">
                  Популярный
                </span>
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

              <button
                type="button"
                onClick={openSignup}
                className={`mt-7 inline-flex items-center justify-center rounded-xl px-6 py-3.5 text-sm font-medium transition-all hover:-translate-y-0.5 ${
                  plan.highlighted
                    ? "bg-white text-brand shadow-soft hover:bg-white/90"
                    : "bg-brand-tint text-brand hover:bg-brand hover:text-white"
                }`}
              >
                Попробовать бесплатно
              </button>

              <ul className="mt-7 flex flex-col gap-3">
                {plan.features.map((feature) => (
                  <li key={feature} className={`flex items-start gap-2.5 text-sm ${plan.highlighted ? "text-white" : "text-ink"}`}>
                    <Check size={18} className={`mt-0.5 shrink-0 ${plan.highlighted ? "text-white" : "text-brand"}`} aria-hidden="true" />
                    {feature}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
