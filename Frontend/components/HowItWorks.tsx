"use client";

import Reveal from "./Reveal";
import { staggerContainer, fadeUp, viewportOnce } from "@/lib/motion";
import { motion } from "framer-motion";

const STEPS = [
  {
    number: "01",
    image: "/step1.webp",
    title: "Расскажите о бизнесе",
    description:
      "Пройдите короткий онбординг: ниша, продукты, аудитория, стиль общения. UCust соберёт «мозг бренда».",
  },
  {
    number: "02",
    image: "/step2.webp",
    title: "ИИ создаёт контент",
    description:
      "Система пишет посты и готовит визуал в вашем стиле и собирает их в контент-план.",
  },
  {
    number: "03",
    image: "/step3.webp",
    title: "Публикация по расписанию",
    description:
      "Подключите соцсети — UCust выложит контент в нужное время. Вы только подтверждаете.",
  },
];

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="mx-auto max-w-(--container-page) px-5 py-12 sm:px-6 sm:py-16 lg:py-20"
    >
      <Reveal>
        <p className="kicker mb-4 text-xs text-brand sm:text-sm">Как это работает</p>
        <h2 className="max-w-2xl text-3xl leading-tight tracking-tight text-ink sm:text-4xl">
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
            className="group rounded-[32px] bg-card p-5 shadow-soft transition-shadow duration-300 hover:shadow-lift sm:p-6"
          >
            <div className="relative mb-5 aspect-[16/10]">
              {/* синяя плита-фон: меньше и позади изображения */}
              <div
                aria-hidden="true"
                className="panel-blue-glass absolute inset-x-[7%] bottom-[2%] top-[34%] rounded-[22px]"
              />
              {/* нормализованный кадр: объект на общей нижней линии, выходит за верх плиты */}
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`${step.image}?v=4`}
                alt=""
                width={1600}
                height={1000}
                aria-hidden="true"
                decoding="async"
                className="absolute inset-0 z-10 h-full w-full object-contain drop-shadow-[0_14px_20px_rgba(31,49,120,0.18)] transition-transform duration-500 ease-out group-hover:scale-[1.03]"
              />
            </div>
            <div className="px-2 sm:px-3">
            <span className="font-display inline-flex h-12 w-12 items-center justify-center rounded-[16px] bg-brand-tint text-lg font-bold text-brand">
              {step.number}
            </span>
            <h3 className="mt-5 text-xl font-bold text-ink sm:text-2xl">
              {step.title}
            </h3>
            <p className="mt-3 text-base leading-relaxed text-ink-muted">
              {step.description}
            </p>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
