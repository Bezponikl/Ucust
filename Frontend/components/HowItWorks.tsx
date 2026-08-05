"use client";

import { useRef, useState } from "react";
import { motion, useScroll, useMotionValueEvent } from "framer-motion";
import SectionHeading from "./SectionHeading";
import { staggerContainer, fadeUp, viewportOnce } from "@/lib/motion";

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

/* Стеклянная рамка с кроссфейдом визуала активного шага. */
function StepVisual({ active }: { active: number }) {
  return (
    <div className="relative aspect-[4/3] w-full">
      <div className="panel-blue-glass absolute inset-0 rounded-[28px]" />
      <span className="font-display absolute left-5 top-5 z-20 inline-flex h-11 w-11 items-center justify-center rounded-[14px] bg-white/80 text-lg font-bold text-brand shadow-soft backdrop-blur-sm">
        {STEPS[active].number}
      </span>
      {STEPS.map((step, i) => (
        <motion.img
          key={step.number}
          src={`${step.image}?v=4`}
          alt={step.title}
          aria-hidden={i !== active}
          decoding="async"
          className="absolute inset-0 z-10 h-full w-full object-contain p-6 drop-shadow-[0_18px_28px_rgba(31,49,120,0.20)]"
          initial={false}
          animate={{ opacity: i === active ? 1 : 0, scale: i === active ? 1 : 0.96 }}
          transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        />
      ))}
    </div>
  );
}

export default function HowItWorks() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(0);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"],
  });

  useMotionValueEvent(scrollYProgress, "change", (p) => {
    const idx = Math.min(STEPS.length - 1, Math.floor(p * STEPS.length));
    setActive(idx);
  });

  // Клик по шагу — доскроллить к его части липкой сцены.
  const goToStep = (i: number) => {
    const el = sectionRef.current;
    if (!el) return;
    const scrollable = el.offsetHeight - window.innerHeight;
    const target =
      el.offsetTop + (scrollable * (i + 0.5)) / STEPS.length;
    window.scrollTo({ top: target, behavior: "smooth" });
  };

  return (
    <section id="how-it-works">
      <div className="mx-auto max-w-(--container-page) px-5 pt-12 sm:px-6 sm:pt-16 lg:pt-20">
        <SectionHeading kicker="Как это работает">
          Три шага — и маркетинг работает сам
        </SectionHeading>
      </div>

      {/* ── Десктоп: липкая сцена (sticky-scroll) ── */}
      <div ref={sectionRef} className="relative hidden lg:block lg:h-[150vh]">
        <div className="sticky top-0 flex min-h-screen items-center">
          <div className="mx-auto grid w-full max-w-(--container-page) grid-cols-2 items-center gap-14 px-6">
            {/* шаги */}
            <div className="relative flex flex-col gap-3 pl-6">
              {/* вертикальный коннектор с бегущим пульсом */}
              <div aria-hidden="true" className="absolute left-0 top-4 bottom-4 w-px bg-border">
                <motion.div
                  className="absolute inset-x-0 rounded-full bg-gradient-to-b from-hero-from via-hero-via to-hero-to"
                  animate={{
                    top: `${(active / STEPS.length) * 100}%`,
                    height: `${(1 / STEPS.length) * 100}%`,
                  }}
                  transition={{ type: "spring", stiffness: 200, damping: 26 }}
                />
              </div>

              {STEPS.map((step, i) => {
                const isActive = i === active;
                return (
                  <button
                    key={step.number}
                    type="button"
                    onClick={() => goToStep(i)}
                    className="rounded-[24px] px-5 py-5 text-left transition-colors duration-300"
                    style={{ background: isActive ? "var(--card)" : "transparent" }}
                  >
                    <motion.div
                      animate={{ opacity: isActive ? 1 : 0.42 }}
                      transition={{ duration: 0.35 }}
                    >
                      <span
                        className={`font-display inline-flex h-12 w-12 items-center justify-center rounded-[16px] text-lg font-bold transition-colors duration-300 ${
                          isActive ? "bg-brand text-white" : "bg-brand-tint text-brand"
                        }`}
                      >
                        {step.number}
                      </span>
                      <h3 className="mt-5 text-2xl font-bold text-ink">{step.title}</h3>
                      <p className="mt-3 max-w-md text-base leading-relaxed text-ink-muted">
                        {step.description}
                      </p>
                    </motion.div>
                  </button>
                );
              })}
            </div>

            {/* визуал */}
            <StepVisual active={active} />
          </div>
        </div>
      </div>

      {/* ── Мобайл/планшет: стек-карточки (фолбэк) ── */}
      <motion.div
        variants={staggerContainer(0.15)}
        initial="hidden"
        whileInView="visible"
        viewport={viewportOnce}
        className="mx-auto mt-12 grid max-w-(--container-page) gap-5 px-5 pb-12 sm:mt-16 sm:px-6 sm:pb-16 md:grid-cols-3 lg:hidden"
      >
        {STEPS.map((step) => (
          <motion.div
            key={step.number}
            variants={fadeUp}
            className="group rounded-[32px] bg-card p-5 shadow-soft transition-shadow duration-300 hover:shadow-lift sm:p-6"
          >
            <div className="relative mb-5 aspect-[16/10]">
              <div
                aria-hidden="true"
                className="panel-blue-glass absolute inset-x-[7%] bottom-[2%] top-[34%] rounded-[22px]"
              />
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
              <h3 className="mt-5 text-xl font-bold text-ink sm:text-2xl">{step.title}</h3>
              <p className="mt-3 text-base leading-relaxed text-ink-muted">{step.description}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
