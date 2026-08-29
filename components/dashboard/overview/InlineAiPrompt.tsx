"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";

export const AI_PROMPT_KEY = "uc_ai_prompt";

const EXAMPLES = [
  "Скидка на завтраки по будням",
  "История нашего бренда",
  "Анонс сезонного меню",
];

// Быстрый вход в генерацию прямо с главной: «опиши — ИИ сделает».
export default function InlineAiPrompt() {
  const router = useRouter();
  const [value, setValue] = useState("");

  const go = (topic: string) => {
    const t = topic.trim();
    try { if (t) sessionStorage.setItem(AI_PROMPT_KEY, t); } catch {}
    router.push("/dashboard/create");
  };

  return (
    <div className="rounded-[24px] border border-border bg-gradient-to-br from-brand/8 via-card to-card p-5 shadow-soft sm:p-6">
      <div className="mb-3 flex items-center gap-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand/12 text-brand">
          <Icon name="sparkles" size={18} aria-hidden="true" />
        </span>
        <div>
          <h2 className="text-base font-bold text-ink sm:text-lg">Создать пост с ИИ</h2>
          <p className="text-xs text-ink-muted">Опишите тему — ИИ напишет и оформит под каждую сеть</p>
        </div>
      </div>

      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") go(value); }}
          placeholder="Например: −20% на выпечку по выходным"
          className="min-w-0 flex-1 rounded-full border border-border bg-surface-soft px-5 py-3 text-sm text-ink outline-none transition focus:border-brand focus:ring-1 focus:ring-brand/25"
        />
        <button
          type="button"
          onClick={() => go(value)}
          className="btn-glass-blue inline-flex shrink-0 items-center justify-center gap-2 px-6 py-3 text-sm font-semibold"
        >
          Создать
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            type="button"
            onClick={() => go(ex)}
            className="rounded-full bg-surface-soft px-3 py-1.5 text-xs text-ink-muted transition hover:text-brand"
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  );
}
