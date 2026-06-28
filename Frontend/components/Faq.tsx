"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";
import Reveal from "./Reveal";

const FAQ_ITEMS = [
  {
    question: "Нужно ли разбираться в маркетинге?",
    answer:
      "Нет. Вы рассказываете о бизнесе своими словами, остальное делает ИИ.",
  },
  {
    question: "В какие соцсети публикует UCust?",
    answer: "VK, Telegram, MAX, Дзен и Одноклассники. Список расширяется.",
  },
  {
    question: "Откуда ИИ знает про мой бизнес?",
    answer:
      "Из короткого онбординга. Вы задаёте нишу, продукты и стиль — система запоминает их в «мозге бренда».",
  },
  {
    question: "Можно ли отредактировать пост перед публикацией?",
    answer:
      "Да. Вы всё видите в контент-плане и подтверждаете перед выходом.",
  },
  {
    question: "Где хранятся мои данные?",
    answer: "На серверах в России, в соответствии с 152-ФЗ.",
  },
  {
    question: "Есть ли бесплатный период?",
    answer: "Да, можно начать без привязки карты.",
  },
];

export default function Faq() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section
      id="faq"
      className="mx-auto max-w-(--container-page) px-5 py-12 sm:px-6 sm:py-16 lg:py-20"
    >
      <Reveal>
        <p className="kicker mb-4 text-xs text-brand sm:text-sm">Вопросы</p>
        <h2 className="max-w-2xl text-3xl leading-tight tracking-tight text-ink sm:text-4xl">
          Частые вопросы
        </h2>
      </Reveal>

      <div className="mt-10 flex flex-col divide-y divide-border rounded-[32px] bg-card px-6 shadow-soft sm:mt-12 sm:px-8 sm:py-2">
        {FAQ_ITEMS.map((item, index) => {
          const isOpen = openIndex === index;
          const panelId = `faq-panel-${index}`;
          const buttonId = `faq-button-${index}`;

          return (
            <div key={item.question}>
              <h3>
                <button
                  id={buttonId}
                  type="button"
                  aria-expanded={isOpen}
                  aria-controls={panelId}
                  onClick={() => setOpenIndex(isOpen ? null : index)}
                  className="flex w-full items-center justify-between gap-4 py-5 text-left text-base font-medium text-ink transition-colors hover:text-brand sm:py-6 sm:text-lg"
                >
                  {item.question}
                  <ChevronDown
                    size={20}
                    aria-hidden="true"
                    className={`shrink-0 text-ink-muted transition-transform duration-300 ${
                      isOpen ? "rotate-180 text-brand" : ""
                    }`}
                  />
                </button>
              </h3>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    id={panelId}
                    role="region"
                    aria-labelledby={buttonId}
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                    className="overflow-hidden"
                  >
                    <p className="pb-5 pr-10 text-sm leading-relaxed text-ink-muted sm:pb-6 sm:text-base">
                      {item.answer}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </section>
  );
}
