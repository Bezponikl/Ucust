"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import { useDashboard } from "./DashboardProvider";
import ProjectLogo from "./ProjectLogo";
import { menuSurfaceClass } from "@/lib/dashboard/surface";
import { dropClass, useDropDirection } from "@/lib/useDropDirection";

export default function ProjectSwitcher() {
  const { data, surfaceStyle, hasProject, projectId, switchProject } = useDashboard();
  // Имя приходит из профиля проекта. Без него проекта по сути нет — в шапке
  // вместо фейкового «Ваш бизнес» показываем кнопку создания.
  const current = data?.businessName?.trim() || null;
  const logo = data?.businessLogo ?? null;
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const dir = useDropDirection(open, ref, 220);
  const router = useRouter();

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  const goCreate = () => {
    try {
      sessionStorage.setItem("uc_show_setup", "1");
    } catch {}
    router.push("/onboarding");
  };

  // Проекта с именем ещё нет: вместо шапки «Ваш проект» — кнопка запуска онбординга.
  if (!hasProject || !current) {
    return (
      <button
        type="button"
        onClick={goCreate}
        aria-label="Создать проект"
        className="flex w-full min-w-0 items-center gap-2.5 rounded-xl border border-dashed border-brand/45 bg-brand/6 px-2.5 py-2 text-left transition hover:border-brand/70 hover:bg-brand/10"
      >
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand text-white" aria-hidden="true">
          <Icon name="plus" size={16} />
        </span>
        <span className="min-w-0 flex-1 leading-tight">
          <span className="block text-[0.625rem] font-semibold uppercase tracking-wider text-brand">Проект</span>
          <span className="block truncate text-sm font-semibold text-ink">Создать проект</span>
        </span>
      </button>
    );
  }

  // Показать всё, что вернул список проектов, а не одного «current».
  const projects = data?.projects ?? [];

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label={`Проект: ${current}. Переключить проект`}
        className={`flex w-full min-w-0 items-center gap-2.5 rounded-xl border px-2.5 py-2 text-left transition ${
          open
            ? "border-brand bg-brand/10 ring-1 ring-brand/25"
            : "border-brand/30 bg-brand/6 hover:border-brand/60 hover:bg-brand/10"
        }`}
      >
        <span className="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-brand text-sm font-bold text-white" aria-hidden="true">
          <ProjectLogo src={logo} name={current} className="h-full w-full" />
        </span>
        <span className="min-w-0 flex-1 leading-tight">
          <span className="block text-[0.625rem] font-semibold uppercase tracking-wider text-brand">Проект</span>
          <span className="block truncate text-sm font-semibold text-ink">{current}</span>
        </span>
        {/* Явная кнопка-«переключить»: раньше стрелка терялась и меню не находили */}
        <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-card/80 text-brand transition-transform ${open ? "rotate-180" : ""}`} aria-hidden="true">
          <Icon name="chevron-down" size={15} />
        </span>
      </button>

      {open && (
        <div className={`absolute left-0 z-50 w-72 overflow-hidden rounded-2xl border border-border p-1.5 shadow-lift ${dropClass(dir)} ${menuSurfaceClass(surfaceStyle)}`}>
          {projects.length === 0 ? (
            <p className="px-3 py-2 text-sm text-ink-muted">Проектов пока нет</p>
          ) : (
            projects.map((b) => {
              const active = b.id === projectId;
              return (
                <button
                  key={b.id}
                  type="button"
                  onClick={() => {
                    setOpen(false);
                    if (b.id !== projectId) void switchProject(b.id);
                  }}
                  className="flex w-full min-w-0 items-center gap-2 rounded-xl px-3 py-2 text-left transition hover:bg-surface-soft"
                >
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-brand-tint text-xs font-bold text-brand" aria-hidden="true">
                    <ProjectLogo src={b.logo} name={b.name} className="h-full w-full" />
                  </span>
                  <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{b.name}</span>
                  {active && <Icon name="check" size={16} className="shrink-0 text-brand" aria-hidden="true" />}
                </button>
              );
            })
          )}
          <div className="my-1 h-px bg-border" />
          <button
            type="button"
            onClick={goCreate}
            className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-medium text-brand hover:bg-surface-soft"
          >
            <Icon name="plus" size={16} aria-hidden="true" /> Добавить проект
          </button>
        </div>
      )}
    </div>
  );
}
