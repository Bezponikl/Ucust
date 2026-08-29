"use client";

import { useState } from "react";
import Icon from "@/components/ui/Icon";
import { formatCompetitor, normalizeUrl, parseCompetitor } from "@/lib/onboarding/competitors";

/**
 * Конкуренты от парсера — это «Название (https://…)» одной строкой. В плоском
 * поле такая строка обрезается на середине домена, а три отдельных блока под
 * типы конкурентов растягивали экран вниз. Поэтому: одна сетка карточек, где
 * название и домен разнесены по строкам, ссылка кликабельна, а правка идёт
 * в самой карточке.
 */
export default function CompetitorList({
  value,
  onChange,
}: {
  value: string[];
  onChange: (next: string[]) => void;
}) {
  // Индекс карточки в режиме правки: -1 — все в режиме просмотра
  const [editing, setEditing] = useState<number>(-1);
  const [draft, setDraft] = useState({ name: "", url: "" });

  const items = value.map(parseCompetitor);

  const startEdit = (i: number) => {
    setEditing(i);
    setDraft({ name: items[i].name, url: items[i].url });
  };

  const commit = (i: number) => {
    const name = draft.name.trim();
    const url = draft.url.trim() ? normalizeUrl(draft.url) : "";
    // Пустую карточку не храним: пользователь передумал её заполнять
    const next = name || url
      ? value.map((v, idx) => (idx === i ? formatCompetitor({ name, url }) : v))
      : value.filter((_, idx) => idx !== i);
    onChange(next);
    setEditing(-1);
  };

  const cancel = (i: number) => {
    // Отмена на только что добавленной пустой карточке убирает её же
    if (!value[i]?.trim()) onChange(value.filter((_, idx) => idx !== i));
    setEditing(-1);
  };

  const remove = (i: number) => {
    onChange(value.filter((_, idx) => idx !== i));
    setEditing(-1);
  };

  const add = () => {
    setDraft({ name: "", url: "" });
    setEditing(value.length);
    onChange([...value, ""]);
  };

  return (
    <div className="flex flex-col gap-3">
      {items.length === 0 && editing === -1 && (
        <p className="rounded-2xl border border-dashed border-border/70 px-4 py-5 text-center text-sm text-ink-muted">
          Пока никого не добавили. По конкурентам ИИ поймёт, чем вы отличаетесь — добавьте хотя бы двоих.
        </p>
      )}

      <ul className="grid gap-2.5 sm:grid-cols-2 [&>li]:min-w-0">
        {items.map((c, i) => {
          const isEditing = editing === i;

          if (isEditing) {
            return (
              <li
                key={i}
                className="min-w-0 rounded-2xl border border-brand/50 bg-card p-3 ring-2 ring-brand/15 sm:p-3.5"
              >
                <div className="flex flex-col gap-2">
                  <input
                    autoFocus
                    value={draft.name}
                    onChange={(e) => setDraft((d) => ({ ...d, name: e.target.value }))}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") commit(i);
                      if (e.key === "Escape") cancel(i);
                    }}
                    placeholder="Название конкурента"
                    aria-label="Название конкурента"
                    className="w-full rounded-xl border border-border/70 bg-surface-soft px-3 py-2 text-sm font-medium text-ink outline-none transition placeholder:font-normal placeholder:text-ink-muted/60 focus:border-brand focus:bg-card"
                  />
                  <div className="flex items-center gap-1.5 rounded-xl border border-border/70 bg-surface-soft px-3 focus-within:border-brand focus-within:bg-card">
                    <Icon name="link" size={14} className="shrink-0 text-ink-muted" aria-hidden="true" />
                    <input
                      value={draft.url}
                      onChange={(e) => setDraft((d) => ({ ...d, url: e.target.value }))}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") commit(i);
                        if (e.key === "Escape") cancel(i);
                      }}
                      placeholder="сайт или соцсеть (необязательно)"
                      aria-label="Ссылка на конкурента"
                      inputMode="url"
                      className="min-w-0 flex-1 bg-transparent py-2 text-sm text-ink outline-none placeholder:text-ink-muted/60"
                    />
                  </div>
                  <div className="flex items-center justify-end gap-1.5">
                    <button
                      type="button"
                      onClick={() => cancel(i)}
                      className="rounded-lg px-3 py-1.5 text-xs font-medium text-ink-muted transition hover:text-ink"
                    >
                      Отмена
                    </button>
                    <button
                      type="button"
                      onClick={() => commit(i)}
                      className="rounded-lg bg-brand px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-brand/90"
                    >
                      Готово
                    </button>
                  </div>
                </div>
              </li>
            );
          }

          return (
            <li
              key={i}
              className="group flex min-w-0 items-center gap-3 rounded-2xl border border-border/70 bg-surface-soft px-3 py-2.5 transition hover:border-brand/40 hover:bg-card"
            >
              {/* Инициал вместо фавикона: не тянем внешние картинки в онбординг */}
              <span
                aria-hidden="true"
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-tint text-sm font-bold uppercase text-brand"
              >
                {c.name.trim().charAt(0) || "?"}
              </span>

              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm font-semibold text-ink">{c.name}</span>
                {c.host ? (
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="inline-flex max-w-full items-center gap-1 truncate text-xs text-ink-muted transition hover:text-brand"
                  >
                    <Icon name="globe" size={11} className="shrink-0" aria-hidden="true" />
                    <span className="truncate">{c.host}</span>
                  </a>
                ) : (
                  // Пустая строка сломала бы ритм карточек, поэтому вместо неё —
                  // приглашение дописать ссылку тем же кликом, что и правка
                  <button
                    type="button"
                    onClick={() => startEdit(i)}
                    className="text-xs text-ink-muted transition hover:text-brand"
                  >
                    + добавить ссылку
                  </button>
                )}
              </span>

              <span className="flex shrink-0 items-center gap-0.5">
                {c.url && (
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={`Открыть сайт: ${c.name}`}
                    title="Открыть сайт"
                    className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-muted transition hover:bg-brand/10 hover:text-brand"
                  >
                    <Icon name="external" size={15} aria-hidden="true" />
                  </a>
                )}
                <button
                  type="button"
                  onClick={() => startEdit(i)}
                  aria-label={`Изменить: ${c.name}`}
                  title="Изменить"
                  className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-muted transition hover:bg-brand/10 hover:text-brand"
                >
                  <Icon name="edit" size={15} aria-hidden="true" />
                </button>
                <button
                  type="button"
                  onClick={() => remove(i)}
                  aria-label={`Удалить: ${c.name}`}
                  title="Удалить"
                  className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-muted transition hover:bg-red-500/10 hover:text-red-500"
                >
                  <Icon name="close" size={15} aria-hidden="true" />
                </button>
              </span>
            </li>
          );
        })}
      </ul>

      <button
        type="button"
        onClick={add}
        className="inline-flex h-10 w-fit items-center gap-1.5 rounded-full border border-dashed border-border px-4 text-sm font-medium text-brand transition hover:border-brand/60 hover:bg-brand/10"
      >
        <Icon name="plus" size={16} aria-hidden="true" /> Добавить конкурента
      </button>
    </div>
  );
}
