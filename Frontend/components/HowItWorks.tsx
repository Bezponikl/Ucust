"use client";

import Reveal from "./Reveal";
import { staggerContainer, fadeUp, viewportOnce } from "@/lib/motion";
import { motion } from "framer-motion";

const STEPS = [
  {
    number: "01",
    title: "Расскажите о бизнесе",
    description:
      "Пройдите короткий онбординг: ниша, продукты, аудитория, стиль общения. UCust соберёт «мозг бренда».",
  },
  {
    number: "02",
    title: "ИИ создаёт контент",
    description:
      "Система пишет посты и готовит визуал в вашем стиле и собирает их в контент-план.",
  },
  {
    number: "03",
    title: "Публикация по расписанию",
    description:
      "Подключите соцсети — UCust выложит контент в нужное время. Вы только подтверждаете.",
  },
];

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="mx-auto max-w-(--container-page) px-5 py-16 sm:px-6 sm:py-24 lg:py-32"
    >
      <Reveal>
        <h2 className="max-w-2xl text-3xl font-extrabold leading-tight tracking-tight text-ink sm:text-4xl">
          Три шага — и маркетинг работает сам
        </h2>
      </Reveal>

      <motion.div
        variants={staggerContainer(0.15)}
        initial="hidden"
        whileInView="visible"
        viewport={viewportOnce}
        className="mt-12 grid gap-5 sm:mt-16 lg:grid-cols-3 lg:gap-6"
      >
        {STEPS.map((step) => (
          <motion.div
            key={step.number}
            variants={fadeUp}
            className="rounded-2xl bg-card p-6 shadow-soft sm:p-8"
          >
            <span className="font-display inline-flex h-11 w-11 items-center justify-center rounded-xl bg-brand-tint text-lg font-bold text-brand">
              {step.number}
            </span>
            <h3 className="mt-5 text-xl font-bold text-ink sm:text-2xl">
              {step.title}
            </h3>
            <p className="mt-3 text-base leading-relaxed text-ink-muted">
              {step.description}
            </p>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
