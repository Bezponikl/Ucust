"use client";

import { motion } from "framer-motion";
import {
  Sparkles,
  CalendarDays,
  Send,
  Percent,
  Star,
  Bot,
  BarChart3,
  Brain,
  type LucideIcon,
} from "lucide-react";
import Reveal from "./Reveal";
import { staggerContainer, fadeUp, viewportOnce } from "@/lib/motion";

const FEATURES: { icon: LucideIcon; title: string; description: string; gradient: string }[] = [
  {
    icon: Sparkles,
    title: "Студия генерации",
    description: "Посты, тексты и визуал по одному запросу.",
    gradient: "from-violet-400 to-purple-600",
  },
  {
    icon: CalendarDays,
    title: "Контент-план",
    description: "Календарь публикаций по всем каналам.",
    gradient: "from-sky-400 to-blue-600",
  },
  {
    icon: Send,
    title: "Автопостинг",
    description: "Выкладывает контент сам, в заданное время.",
    gradient: "from-emerald-400 to-teal-500",
  },
  {
    icon: Percent,
    title: "Акции и промо",
    description: "Готовые кампании со скидками и спецпредложениями.",
    gradient: "from-amber-300 to-orange-500",
  },
  {
    icon: Star,
    title: "Отзывы",
    description: "Собирает отзывы и предлагает ответы.",
    gradient: "from-pink-400 to-rose-500",
  },
  {
    icon: Bot,
    title: "Чат-бот",
    description: "Отвечает клиентам в ваших каналах.",
    gradient: "from-indigo-400 to-blue-700",
  },
  {
    icon: BarChart3,
    title: "Аналитика",
    description: "Показывает, что работает, и что улучшить.",
    gradient: "from-teal-400 to-cyan-600",
  },
  {
    icon: Brain,
    title: "Мозг бренда",
    description: "Помнит ваш стиль и пишет как вы.",
    gradient: "from-fuchsia-400 to-purple-600",
  },
];

export default function Features() {
  return (
    <section id="features">
      <div className="mx-auto max-w-(--container-page) px-5 py-16 sm:px-6 sm:py-24 lg:py-32">
        <Reveal>
          <h2 className="max-w-2xl text-3xl font-extrabold leading-tight tracking-tight text-ink sm:text-4xl">
            Всё, что нужно для соцсетей, в одном месте
          </h2>
        </Reveal>

        <motion.div
          variants={staggerContainer(0.08)}
          initial="hidden"
          whileInView="visible"
          viewport={viewportOnce}
          className="mt-12 grid grid-cols-1 gap-4 sm:mt-16 sm:grid-cols-2 lg:grid-cols-4"
        >
          {FEATURES.map(({ icon: Icon, title, description, gradient }) => (
            <motion.div
              key={title}
              variants={fadeUp}
              className="group rounded-2xl bg-card p-6 shadow-soft transition-transform duration-200 hover:-translate-y-0.5"
            >
              <span className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br shadow-soft ${gradient}`}>
                <Icon size={20} className="text-white" aria-hidden="true" />
              </span>
              <h3 className="mt-4 text-base font-bold text-ink sm:text-lg">
                {title}
              </h3>
              <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">
                {description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
