"use client";

import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import Icon from "./ui/Icon";
import Reveal from "./Reveal";
import SectionHeading from "./SectionHeading";
import { useAuthModal } from "./AuthModalProvider";
import TariffInfoModal from "./TariffInfoModal";
import { staggerContainer, fadeUp, viewportOnce } from "@/lib/motion";

type Accent = "blue" | "gradient" | "purple";

// Цвет названия плана + галочек фич (в духе референса: каждый план — свой акцент)
const ACCENT: Record<Accent, { name: string; check: string }> = {
  blue: { name: "text-brand", check: "text-brand" },
  gradient: { name: "text-gradient", check: "text-brand" },
  purple: { name: "text-brand-purple", check: "text-brand-purple" },
};

const PLANS: {
  name: string;
  price: number;
  tagline: string;
  features: string[];
  highlighted: boolean;
  accent: Accent;
}[] = [
  {
    name: "Старт",
    price: 1500,
    tagline: "Для одного бизнеса.",
    accent: "blue",
    features: [
      "1 бизнес",
      "До 12 постов в месяц",
      "Все соцсети без ограничений",
      "Генерация фото",
      "Посты по контент-плану",
      "Базовая аналитика",
      "Email-поддержка",
    ],
    highlighted: false,
  },
  {
    name: "Бизнес",
    price: 3500,
    tagline: "Для регулярного ведения.",
    accent: "gradient",
    features: [
      "3 бизнеса",
      "До 30 постов в месяц",
      "Все соцсети без ограничений",
      "Генерация фото и видео",
      "Генерация постов по запросу",
      "Расширенная аналитика",
      "Приоритетная поддержка",
    ],
    highlighted: true,
  },
];

const YEARLY_DISCOUNT = 0.1;
const fmt = (n: number) => n.toLocaleString("ru-RU");
/** Цена за месяц с учётом выбранного периода (год — дешевле на 10%). */
const monthlyPrice = (base: number, period: "month" | "year") =>
  period === "year" ? Math.round((base * (1 - YEARLY_DISCOUNT)) / 10) * 10 : base;

export default function Pricing() {
  const { openSignup } = useAuthModal();
  const reduce = useReducedMotion();
  const animate = !reduce;
  const [period, setPeriod] = useState<"month" | "year">("month");
  const [tariffInfoOpen, setTariffInfoOpen] = useState(false);

  return (
    <section id="pricing">
      <div className="mx-auto max-w-(--container-page) px-5 py-12 sm:px-6 sm:py-16 lg:py-20">
        <SectionHeading kicker="Тарифы">
          Простые тарифы без сюрпризов
        </SectionHeading>

        <Reveal className="mt-8 flex justify-center sm:mt-10">
          <div
            role="radiogroup"
            aria-label="Период оплаты"
            className="inline-flex items-center gap-1 rounded-full border border-border bg-surface-soft p-1"
          >
            <button
              type="button"
              role="radio"
              aria-checked={period === "month"}
              onClick={() => setPeriod("month")}
              className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                period === "month" ? "bg-card text-ink shadow-soft" : "text-ink-muted hover:text-ink"
              }`}
            >
              Месяц
            </button>
            <button
              type="button"
              role="radio"
              aria-checked={period === "year"}
              onClick={() => setPeriod("year")}
              className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                period === "year" ? "bg-card text-ink shadow-soft" : "text-ink-muted hover:text-ink"
              }`}
            >
              Год
              <span className="rounded-full bg-brand-tint px-2 py-0.5 text-xs font-semibold text-brand">
                −10%
              </span>
            </button>
          </div>
        </Reveal>

        <motion.div
          variants={staggerContainer(0.1)}
          initial="hidden"
          whileInView="visible"
          viewport={viewportOnce}
          className="mt-12 mx-auto grid max-w-6xl gap-6 sm:mt-16 sm:grid-cols-2 lg:grid-cols-3"
        >
          {PLANS.map((plan) => {
            const a = ACCENT[plan.accent];
            return (
              <motion.div
                key={plan.name}
                variants={fadeUp}
                className={`relative isolate flex flex-col rounded-[28px] border p-7 sm:p-8 transition-shadow duration-300 ${
                  plan.highlighted
                    ? "border-brand/40 bg-card shadow-lift ring-1 ring-brand/20 lg:-translate-y-2"
                    : "border-border bg-card/80 shadow-soft hover:shadow-lift"
                }`}
              >
                {plan.highlighted && (
                  <div
                    aria-hidden="true"
                    className="pointer-events-none absolute inset-0 -z-10 overflow-hidden rounded-[28px]"
                  >
                    <motion.span
                      className="absolute -top-1/4 left-[8%] h-56 w-56 rounded-full bg-brand/15 blur-3xl"
                      animate={
                        animate
                          ? { x: [0, 50, 0], y: [0, 30, 0], opacity: [0.4, 0.75, 0.4] }
                          : undefined
                      }
                      transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
                    />
                  </div>
                )}

                <div className="mb-5 flex items-start justify-between gap-3">
                  <h3 className={`font-display text-2xl font-extrabold tracking-tight ${a.name}`}>
                    {plan.name}
                  </h3>
                  {plan.highlighted && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-brand/12 px-3 py-1 text-xs font-semibold text-brand ring-1 ring-brand/20">
                      <Icon name="sparkles" size={12} /> Популярный
                    </span>
                  )}
                </div>

                <p className="text-sm leading-relaxed text-ink-muted">{plan.tagline}</p>

                <p className="mt-6 flex items-baseline gap-1.5">
                  <span className="font-display text-5xl font-extrabold tracking-tight text-ink sm:text-6xl">
                    {fmt(monthlyPrice(plan.price, period))}
                  </span>
                  <span className="font-display text-sm text-ink-muted">₽/мес</span>
                </p>
                <p className="mt-1.5 text-xs text-ink-muted">
                  {period === "year"
                    ? `${fmt(monthlyPrice(plan.price, period) * 12)} ₽ в год · экономия 10%`
                    : "при ежемесячной оплате"}
                </p>

                <ul className="mt-7 mb-8 flex flex-col gap-3.5 border-t border-border pt-6">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2.5 text-sm text-ink">
                      <Icon name="check-bold" size={20} className={`shrink-0 ${a.check}`} />
                      {feature}
                    </li>
                  ))}
                </ul>

                <button
                  type="button"
                  onClick={openSignup}
                  className={`mt-auto inline-flex items-center justify-center px-6 py-3.5 text-sm font-semibold ${
                    plan.highlighted ? "btn-glass-blue" : "btn-glass"
                  }`}
                >
                  Попробовать бесплатно
                </button>
              </motion.div>
            );
          })}

          {/* Гибкий настраиваемый тариф */}
          <motion.div
            variants={fadeUp}
            className="relative isolate flex flex-col rounded-[28px] border border-border bg-card/80 p-7 shadow-soft transition-shadow duration-300 hover:shadow-lift sm:p-8"
          >
            <div className="mb-5 flex items-center gap-2.5">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[14px] bg-brand-purple/12 text-brand-purple">
                <Icon name="sliders" size={20} />
              </span>
              <h3 className="font-display text-2xl font-extrabold tracking-tight text-brand-purple">
                Свой тариф
              </h3>
            </div>

            <p className="text-sm leading-relaxed text-ink-muted">Настройте под свои нужды.</p>

            <p className="mt-6 flex items-baseline gap-1.5">
              <span className="font-display text-2xl font-medium text-ink-muted">от</span>
              <span className="font-display text-5xl font-extrabold tracking-tight text-ink sm:text-6xl">
                {fmt(monthlyPrice(1500, period))}
              </span>
              <span className="font-display text-sm text-ink-muted">₽/мес</span>
            </p>
            <p className="mt-1.5 text-xs text-ink-muted">Цена зависит от выбранных опций</p>

            <ul className="mt-7 mb-8 flex flex-col gap-3.5 border-t border-border pt-6">
              {[
                "Любое число постов и бизнесов",
                "Видео, акции и водяной знак бренда",
                "Единые входящие, ИИ-ответы и CRM",
                "Команда и персональный менеджер",
                "Оплата только за нужные опции",
              ].map((feature) => (
                <li key={feature} className="flex items-center gap-2.5 text-sm text-ink">
                  <Icon name="check-bold" size={20} className="shrink-0 text-brand-purple" />
                  {feature}
                </li>
              ))}
            </ul>

            <button
              type="button"
              onClick={() => setTariffInfoOpen(true)}
              className="btn-glass mt-auto inline-flex items-center justify-center px-6 py-3.5 text-sm font-semibold"
            >
              Настроить свой тариф
            </button>
          </motion.div>
        </motion.div>
      </div>

      <TariffInfoModal
        open={tariffInfoOpen}
        onClose={() => setTariffInfoOpen(false)}
        onStart={() => {
          setTariffInfoOpen(false);
          openSignup();
        }}
      />
    </section>
  );
}
