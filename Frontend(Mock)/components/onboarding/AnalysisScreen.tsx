"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Icon from "@/components/ui/Icon";

const STAGES = [
  "Читаем, что вы рассказали",
  "Ищем нишу и аудиторию",
  "Собираем сильные стороны",
  "Формулируем стиль общения",
];

const STAGE_MS = 620;

export default function AnalysisScreen({ onDone }: { onDone: () => void }) {
  const [done, setDone] = useState(0);

  useEffect(() => {
    const tick = setInterval(() => setDone((d) => Math.min(d + 1, STAGES.length)), STAGE_MS);
    const finish = setTimeout(onDone, STAGE_MS * STAGES.length + 500);
    return () => { clearInterval(tick); clearTimeout(finish); };
  }, [onDone]);

  return (
    <div className="flex flex-col items-center py-16 text-center">
      {/* Пульс вокруг значка: видно, что работа идёт, но экран не мигает лишним */}
      <span className="relative mb-6 flex h-20 w-20 items-center justify-center">
        <motion.span
          className="absolute inset-0 rounded-3xl bg-brand/18"
          animate={{ scale: [1, 1.18, 1], opacity: [0.55, 0.15, 0.55] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
        <span className="relative flex h-16 w-16 items-center justify-center rounded-3xl bg-brand/15 text-brand">
          <Icon name="brain" size={30} aria-hidden="true" />
        </span>
      </span>

      <h1 className="text-2xl font-bold text-ink sm:text-3xl">Собираем профиль бренда</h1>
      <p className="mt-2 text-sm text-ink-muted">Несколько секунд — и всё будет готово к проверке</p>

      <ul className="mt-8 flex w-full max-w-xs flex-col gap-3 text-left">
        {STAGES.map((s, i) => {
          const isDone = i < done;
          const active = i === done;
          return (
            <li
              key={s}
              className={`flex items-center gap-3 text-sm transition ${isDone || active ? "text-ink" : "text-ink-muted/50"}`}
            >
              <span
                className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full ${
                  isDone ? "bg-success text-white" : active ? "bg-brand/15 text-brand" : "bg-surface-soft text-ink-muted/50"
                }`}
              >
                {isDone ? (
                  <Icon name="check" size={12} aria-hidden="true" />
                ) : active ? (
                  <Icon name="refresh" size={12} className="animate-spin" aria-hidden="true" />
                ) : (
                  <span className="h-1.5 w-1.5 rounded-full bg-current" />
                )}
              </span>
              {s}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
