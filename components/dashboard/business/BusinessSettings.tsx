"use client";

import { useEffect, useRef, useState, type ChangeEvent } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import { CHANNELS } from "@/lib/channels";
import { businessFromOnboarding, CATEGORIES, EMPTY_BUSINESS, type BusinessProfile } from "@/lib/dashboard/businesses";
import { loadOnboarding } from "@/lib/onboarding/storage";
import { SettingsCard, Field, TextArea, SelectField, SaveButton } from "@/components/dashboard/settings/primitives";
import TimeInput from "@/components/ui/TimeInput";
import ModalShell from "@/components/ModalShell";
import { toast } from "@/lib/toast";
import { toMessage } from "@/lib/api/errors";
import { businessToProjectPatch, projectToBusiness } from "@/lib/api/mapBusiness";
import { deleteProject, getProject, updateProject, uploadLogo } from "@/lib/api/projects";
import type { ProjectResponse } from "@/lib/api/types";
import { useDashboard } from "@/components/dashboard/DashboardProvider";
import { isProjectFrozen, setProjectFrozen } from "@/lib/dashboard/projectState";

const WEEK = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

export default function BusinessSettings() {
  const router = useRouter();
  const { projectId, reloadWorkspace } = useDashboard();
  const [b, setB] = useState<BusinessProfile>(EMPTY_BUSINESS);
  /** Ответ бэка целиком: при сохранении из него берутся поля, которых нет на экране. */
  const [project, setProject] = useState<ProjectResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Пока проекта на бэке нет, показываем то, что осталось от онбординга.
  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect */
    if (!projectId) {
      setB(businessFromOnboarding(loadOnboarding()) ?? EMPTY_BUSINESS);
      return;
    }

    let cancelled = false;
    setLoading(true);
    void getProject(projectId)
      .then((p) => {
        if (cancelled) return;
        setProject(p);
        setB(projectToBusiness(p));
      })
      .catch((err) => {
        if (!cancelled) toast(toMessage(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [projectId]);

  const logoInput = useRef<HTMLInputElement>(null);
  const urls = useRef<string[]>([]);
  useEffect(() => () => urls.current.forEach((u) => URL.revokeObjectURL(u)), []);

  const set = <K extends keyof BusinessProfile>(k: K, v: BusinessProfile[K]) => setB((p) => ({ ...p, [k]: v }));

  const onLogo = async (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;

    // Показываем выбранный файл сразу, не дожидаясь ответа сервера.
    const u = URL.createObjectURL(f);
    urls.current.push(u);
    set("logo", u);

    if (!projectId) return;
    try {
      const url = await uploadLogo(projectId, f);
      if (url) set("logo", url);
      await reloadWorkspace();
    } catch (err) {
      toast(toMessage(err));
    }
  };

  const toggleDay = (d: number) => set("daysOff", b.daysOff.includes(d) ? b.daysOff.filter((x) => x !== d) : [...b.daysOff, d]);
  const toggleSocial = (id: string) => set("socials", b.socials.map((s) => s.id === id ? { ...s, connected: !s.connected } : s));

  const save = async () => {
    if (!projectId) {
      toast("Сначала создайте проект — данные пока некуда сохранить");
      return;
    }
    try {
      const updated = await updateProject(projectId, businessToProjectPatch(b, project));
      setProject(updated);
      setB(projectToBusiness(updated));
      await reloadWorkspace();
    } catch (err) {
      toast(toMessage(err));
    }
  };

  // Заморозка — мягкая альтернатива удалению: публикации встают на паузу,
  // данные остаются. Удаление доступно и из замороженного состояния.
  const [frozen, setFrozen] = useState(false);
  const [confirmFreeze, setConfirmFreeze] = useState(false);

  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect */
    setFrozen(isProjectFrozen(projectId));
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [projectId]);

  const toggleFreeze = () => {
    const next = !frozen;
    setProjectFrozen(projectId, next);
    setFrozen(next);
    setConfirmFreeze(false);
    toast(next ? "Бизнес заморожен — публикации на паузе" : "Бизнес снова активен");
  };

  const [confirmDelete, setConfirmDelete] = useState(false);
  const doDelete = async () => {
    setConfirmDelete(false);
    if (!projectId) {
      toast("Бизнес удалён");
      return;
    }
    try {
      await deleteProject(projectId);
      await reloadWorkspace();
      toast("Бизнес удалён");
      router.push("/dashboard");
    } catch (err) {
      toast(toMessage(err));
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-xl font-bold text-ink sm:text-2xl">Профиль бизнеса</h1>
        <p className="mt-0.5 text-sm text-ink-muted" aria-live="polite">
          {loading ? "Загружаем данные проекта…" : "Данные бизнеса и подключённые каналы"}
        </p>
      </div>

      {frozen && (
        <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-brand/30 bg-brand/8 px-4 py-3">
          <Icon name="clock" size={18} className="shrink-0 text-brand" aria-hidden="true" />
          <p className="min-w-0 flex-1 text-sm text-ink">
            <span className="font-semibold">Бизнес заморожен.</span>{" "}
            Публикации и автоответы на паузе, данные сохранены.
          </p>
          <button type="button" onClick={toggleFreeze} className="btn-glass-blue shrink-0 px-4 py-2 text-xs font-semibold">
            Возобновить
          </button>
        </div>
      )}

      {/* Шапка: лого + название — без карточки */}
      <div className="flex items-center gap-5">
        <span className="relative flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-2xl bg-brand-tint text-3xl font-bold text-brand">
          {b.logo ? <Image src={b.logo} alt="" fill unoptimized={b.logo.startsWith("blob:")} className="object-cover" /> : b.name.slice(0, 1)}
        </span>
        <div className="min-w-0">
          <p className="truncate text-xl font-bold text-ink">{b.name || "Название бизнеса"}</p>
          <p className="text-sm text-ink-muted">{b.category}</p>
          <div className="mt-2 flex items-center gap-3 text-sm">
            <button type="button" onClick={() => logoInput.current?.click()} className="inline-flex items-center gap-1.5 font-medium text-brand hover:text-brand-hover"><Icon name="image-plus" size={15} /> Загрузить</button>
            {b.logo && <button type="button" onClick={() => set("logo", undefined)} className="text-ink-muted hover:text-ink">Удалить</button>}
          </div>
        </div>
        <input ref={logoInput} type="file" accept="image/*" hidden onChange={onLogo} />
      </div>

      {/* Основное */}
      <SettingsCard title="Основное">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Название компании" value={b.name} onChange={(v) => set("name", v)} />
          <SelectField label="Сфера деятельности" value={b.category} onChange={(v) => set("category", v)} options={CATEGORIES} />
          <Field label="Адрес" value={b.address} onChange={(v) => set("address", v)} />
          <Field label="Телефон" value={b.phone} onChange={(v) => set("phone", v)} />
          <Field label="Сайт" value={b.site} onChange={(v) => set("site", v)} />
        </div>
        <div className="mt-4">
          <TextArea label="Описание бизнеса" value={b.description} onChange={(v) => set("description", v)} placeholder="Опишите, чем занимается ваш бизнес" />
        </div>
      </SettingsCard>

      {/* Часы работы */}
      <SettingsCard title="Часы работы">
        {/* Время вписывается вручную — те же правила, что и у публикаций */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <TimeInput
            label="Время начала"
            ariaLabel="Время начала работы"
            variant="settings"
            value={b.workStart}
            onChange={(v) => set("workStart", v)}
          />
          <TimeInput
            label="Время окончания"
            ariaLabel="Время окончания работы"
            variant="settings"
            value={b.workEnd}
            onChange={(v) => set("workEnd", v)}
          />
        </div>
        <div className="mt-4">
          <span className="mb-1.5 block text-sm font-semibold text-ink">Выходные дни</span>
          <div className="flex flex-wrap gap-2">
            {WEEK.map((w, i) => {
              const off = b.daysOff.includes(i);
              return (
                <button key={w} type="button" aria-pressed={off} onClick={() => toggleDay(i)}
                  className={`rounded-xl border px-3.5 py-2 text-sm font-medium transition ${off ? "border-brand bg-brand/8 text-brand" : "border-border bg-surface-soft text-ink-muted hover:text-ink"}`}>
                  {w}
                </button>
              );
            })}
          </div>
        </div>
      </SettingsCard>

      {/* Соцсети */}
      <SettingsCard title="Соцсети бизнеса" desc="Подключённые каналы для публикаций">
        <ul className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
          {b.socials.map((s) => {
            const ch = CHANNELS[s.id];
            return (
              <li key={s.id} className="flex items-center gap-3 rounded-2xl border border-border bg-surface-soft/60 px-3.5 py-3 backdrop-blur-sm">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-border bg-card">
                  {ch.icon && ch.iconType !== "wordmark"
                    ? <Image src={ch.icon} alt="" width={22} height={22} className="h-[1.375rem] w-[1.375rem] object-contain" aria-hidden="true" />
                    : <span className="h-[1.375rem] w-[1.375rem] rounded" style={{ backgroundColor: ch.colorVar }} aria-hidden="true" />}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-ink">{ch.label}</p>
                  <p className="flex items-center gap-1.5 text-xs text-ink-muted">
                    {s.connected
                      ? <><span className="h-1.5 w-1.5 rounded-full bg-success" aria-hidden="true" /> Подключено</>
                      : "Не подключено"}
                  </p>
                </div>
                {s.connected ? (
                  <button type="button" onClick={() => toggleSocial(s.id)} className="btn-glass shrink-0 px-4 py-1.5 text-xs font-semibold">Отключить</button>
                ) : (
                  <button type="button" onClick={() => toggleSocial(s.id)} className="btn-glass-blue shrink-0 px-4 py-1.5 text-xs font-semibold">Подключить</button>
                )}
              </li>
            );
          })}
        </ul>
      </SettingsCard>

      {/* Действия */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <SaveButton onSave={() => void save()} />
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          {/* Заморозка стоит перед удалением: чаще нужна именно пауза */}
          <button
            type="button"
            onClick={() => (frozen ? toggleFreeze() : setConfirmFreeze(true))}
            className="inline-flex items-center gap-2 self-start rounded-xl px-4 py-3 text-sm font-semibold text-ink-muted transition hover:bg-surface-soft hover:text-ink"
          >
            <Icon name={frozen ? "play" : "clock"} size={16} aria-hidden="true" />
            {frozen ? "Возобновить бизнес" : "Заморозить бизнес"}
          </button>
          <button type="button" onClick={() => setConfirmDelete(true)} className="inline-flex items-center gap-2 self-start rounded-xl px-4 py-3 text-sm font-semibold text-red-500 transition hover:bg-red-500/10">
            <Icon name="trash" size={16} aria-hidden="true" /> Удалить бизнес
          </button>
        </div>
      </div>

      {/* Подтверждение заморозки */}
      <ModalShell open={confirmFreeze} onClose={() => setConfirmFreeze(false)} labelledBy="freeze-biz-title">
        <div className="flex flex-col items-center text-center">
          <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-brand/12 text-brand">
            <Icon name="clock" size={26} aria-hidden="true" />
          </span>
          <h2 id="freeze-biz-title" className="text-lg font-bold text-ink">Заморозить бизнес?</h2>
          <p className="mt-1.5 text-sm text-ink-muted">
            Публикации и автоответы для «{b.name}» встанут на паузу. Данные, контент и статистика
            останутся на месте — вернуть бизнес в работу можно в любой момент.
          </p>
          <div className="mt-6 flex w-full flex-col gap-2 sm:flex-row-reverse">
            <button
              type="button"
              onClick={toggleFreeze}
              className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 px-5 py-3 text-sm font-semibold"
            >
              <Icon name="clock" size={16} aria-hidden="true" /> Заморозить
            </button>
            <button
              type="button"
              onClick={() => setConfirmFreeze(false)}
              className="inline-flex flex-1 items-center justify-center rounded-full border border-border px-5 py-3 text-sm font-semibold text-ink transition hover:bg-surface-soft"
            >
              Отмена
            </button>
          </div>
        </div>
      </ModalShell>

      {/* Подтверждение удаления бизнеса */}
      <ModalShell open={confirmDelete} onClose={() => setConfirmDelete(false)} labelledBy="del-biz-title">
        <div className="flex flex-col items-center text-center">
          <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-500/12 text-red-500">
            <Icon name="trash" size={26} aria-hidden="true" />
          </span>
          <h2 id="del-biz-title" className="text-lg font-bold text-ink">Удалить бизнес?</h2>
          <p className="mt-1.5 text-sm text-ink-muted">
            Бизнес «{b.name}» и все связанные с ним данные будут удалены безвозвратно. Это действие нельзя отменить.
          </p>
          <div className="mt-6 flex w-full flex-col gap-2 sm:flex-row-reverse">
            <button
              type="button"
              onClick={doDelete}
              className="inline-flex flex-1 items-center justify-center gap-2 rounded-full bg-red-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-red-600"
            >
              <Icon name="trash" size={16} aria-hidden="true" /> Удалить
            </button>
            <button
              type="button"
              onClick={() => setConfirmDelete(false)}
              className="inline-flex flex-1 items-center justify-center rounded-full border border-border px-5 py-3 text-sm font-semibold text-ink transition hover:bg-surface-soft"
            >
              Отмена
            </button>
          </div>
        </div>
      </ModalShell>
    </div>
  );
}
