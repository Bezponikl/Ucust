"use client";

import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";
import { seedDemoProject } from "@/lib/onboarding/demo";

const STEPS: { icon: IconName; title: string; text: string }[] = [
  { icon: "brain",     title: "Профиль бизнеса", text: "Расскажите о деле своими словами — ИИ соберёт «мозг бренда»" },
  { icon: "link",      title: "Соцсети",         text: "Подключите VK, Telegram и остальные площадки" },
  { icon: "sparkles",  title: "Первый пост",     text: "UCust напишет и опубликует — вам останется подтвердить" },
];

/** Бледный виджет-заглушка: показывает, что появится на месте блока. */
function GhostStat({ label }: { label: string }) {
  return (
    <div className="rounded-[20px] border border-dashed border-border bg-card/50 p-4 sm:p-5">
      <div className="mb-3 flex items-center justify-between gap-2">
        <span className="h-9 w-9 shrink-0 rounded-xl bg-surface-soft" />
        <span className="truncate text-xs font-medium text-ink-muted/70">{label}</span>
      </div>
      <span className="font-display text-2xl font-extrabold text-ink-muted/40">—</span>
    </div>
  );
}

function GhostPanel({ title, icon, hint }: { title: string; icon: IconName; hint: string }) {
  return (
    <div className="flex min-h-52 flex-col rounded-[24px] border border-dashed border-border bg-card/50 p-5">
      <p className="mb-4 flex items-center gap-2 text-sm font-semibold text-ink-muted/80">
        <Icon name={icon} size={15} aria-hidden="true" /> {title}
      </p>
      <div className="flex flex-col gap-2.5">
        <span className="h-3.5 w-3/4 rounded-full bg-surface-soft" />
        <span className="h-3.5 w-full rounded-full bg-surface-soft" />
        <span className="h-3.5 w-2/3 rounded-full bg-surface-soft" />
      </div>
      <p className="mt-auto pt-4 text-xs text-ink-muted/70">{hint}</p>
    </div>
  );
}

export default function EmptyOverview() {
  const router = useRouter();

  // Демо-профиль лежит в sessionStorage, его читают провайдеры при монтировании —
  // поэтому не router.push, а полная перезагрузка страницы.
  const showDemo = () => {
    seedDemoProject();
    window.location.assign("/dashboard");
  };

  return (
    <div className="flex flex-col gap-6 sm:gap-8">
      {/* Приглашение — единственный акцент на экране */}
      <section
        data-tour="overview"
        className="overflow-hidden rounded-[28px] border border-border bg-gradient-to-br from-brand/10 via-card to-card p-6 shadow-soft sm:p-8"
      >
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-xl">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-brand/12 px-3 py-1 text-xs font-semibold text-brand">
              <Icon name="sparkles" size={13} aria-hidden="true" /> Аккаунт создан
            </span>
            <h1 className="mt-3 text-2xl font-bold text-ink sm:text-[1.75rem]">
              Добро пожаловать в UCust
            </h1>
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">
              Осталось рассказать о бизнесе — на это уйдёт около трёх минут. После этого ИИ
              соберёт профиль бренда, предложит контент-план и начнёт вести соцсети за вас.
            </p>

            <div className="mt-5 flex flex-col gap-2 sm:flex-row sm:items-center">
              <button
                type="button"
                data-tour="create-project"
                onClick={() => router.push("/onboarding")}
                className="btn-glass-blue inline-flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold"
              >
                <Icon name="plus" size={16} aria-hidden="true" /> Создать профиль проекта
              </button>
              <button
                type="button"
                onClick={showDemo}
                className="inline-flex items-center justify-center gap-2 rounded-full px-5 py-3.5 text-sm font-medium text-ink-muted transition hover:text-ink"
              >
                <Icon name="eye" size={15} aria-hidden="true" /> Посмотреть на демо-проекте
              </button>
            </div>
          </div>

          {/* Три шага запуска */}
          <ol className="flex shrink-0 flex-col gap-3 lg:w-80">
            {STEPS.map((s, i) => (
              <li key={s.title} className="flex items-start gap-3 rounded-2xl border border-border bg-card/70 p-3.5">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand/10 text-brand">
                  <Icon name={s.icon} size={17} aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-ink">
                    <span className="text-ink-muted">{i + 1}. </span>{s.title}
                  </p>
                  <p className="mt-0.5 text-xs leading-relaxed text-ink-muted">{s.text}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* Каркас будущего дашборда — некликабельный, приглушённый */}
      <div aria-hidden="true" className="pointer-events-none flex select-none flex-col gap-6 opacity-70 sm:gap-8">
        <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
          <GhostStat label="Просмотры" />
          <GhostStat label="Вовлечённость" />
          <GhostStat label="Новые подписчики" />
          <GhostStat label="Отзывы" />
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 [&>*]:min-w-0">
          <GhostPanel
            title="Контент-план недели"
            icon="calendar"
            hint="Появится сразу после создания профиля — ИИ предложит темы на неделю вперёд"
          />
          <GhostPanel
            title="Рекомендации UCust"
            icon="brain"
            hint="Здесь будут подсказки: что опубликовать, кому ответить, какую акцию запустить"
          />
        </div>
      </div>
    </div>
  );
}
