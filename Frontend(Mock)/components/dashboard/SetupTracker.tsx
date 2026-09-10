"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";
import { useDashboard } from "./DashboardProvider";

type Step = { id: string; label: string; href: string; icon: IconName };

// Шаги активации нового проекта. Порядок = порядок «дожатия» пользователя.
const STEPS: Step[] = [
  { id: "connect", label: "Подключить соцсеть", href: "/dashboard/settings", icon: "link" },
  { id: "first-post", label: "Создать первый пост", href: "/dashboard/create", icon: "sparkles" },
  { id: "autopost", label: "Запустить автопостинг", href: "/dashboard/content", icon: "calendar-check" },
];

const DONE_KEY = "uc_setup_done";
const DISMISS_KEY = "uc_setup_dismissed";

export default function SetupTracker() {
  const { hasProject } = useDashboard();
  const [done, setDone] = useState<string[]>([]);
  const [dismissed, setDismissed] = useState(true); // по умолчанию скрыт до гидрации (анти-мелькание)
  const [enabled, setEnabled] = useState(false); // показываем только после регистрации / добавления бизнеса
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      setDone(JSON.parse(sessionStorage.getItem(DONE_KEY) ?? "[]"));
      setDismissed(sessionStorage.getItem(DISMISS_KEY) === "1");
      setEnabled(sessionStorage.getItem("uc_show_setup") === "1");
    } catch {}
    setReady(true);
  }, []);

  const persistDone = (next: string[]) => {
    setDone(next);
    try { sessionStorage.setItem(DONE_KEY, JSON.stringify(next)); } catch {}
  };
  const toggle = (id: string) =>
    persistDone(done.includes(id) ? done.filter((d) => d !== id) : [...done, id]);
  const dismiss = () => {
    setDismissed(true);
    try { sessionStorage.setItem(DISMISS_KEY, "1"); } catch {}
  };

  const count = done.length;
  const allDone = count === STEPS.length;
  // До создания профиля трекер не нужен: там свой призыв на пустом дашборде.
  if (!ready || !enabled || !hasProject || dismissed || allDone) return null;

  return (
    <aside
      className="fixed right-4 bottom-24 z-40 w-[300px] max-w-[calc(100vw-2rem)] rounded-2xl border border-border bg-card p-4 shadow-lift lg:bottom-6"
      aria-label="Прогресс настройки"
    >
      <div className="mb-2.5 flex items-center justify-between">
        <span className="text-sm font-bold text-ink">Завершить настройку</span>
        <button type="button" onClick={dismiss} aria-label="Скрыть" className="text-ink-muted transition hover:text-ink">
          <Icon name="close" size={16} />
        </button>
      </div>

      <div className="mb-3 flex items-center gap-2">
        <span className="text-xs font-medium text-ink-muted">{count} из {STEPS.length}</span>
        <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-soft">
          <span
            className="block h-full rounded-full bg-brand transition-all duration-500"
            style={{ width: `${(count / STEPS.length) * 100}%` }}
          />
        </span>
      </div>

      <ul className="flex flex-col gap-1">
        {STEPS.map((s) => {
          const isDone = done.includes(s.id);
          return (
            <li key={s.id} className="flex items-center gap-2.5">
              <button
                type="button"
                onClick={() => toggle(s.id)}
                aria-pressed={isDone}
                aria-label={isDone ? "Отметить невыполненным" : "Отметить выполненным"}
                className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition ${
                  isDone ? "border-brand bg-brand text-white" : "border-border text-transparent hover:border-brand"
                }`}
              >
                <Icon name="check-bold" size={11} />
              </button>
              <Link
                href={s.href}
                className={`flex-1 rounded-lg px-1 py-1.5 text-sm transition hover:text-brand ${
                  isDone ? "text-ink-muted line-through" : "text-ink"
                }`}
              >
                {s.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
