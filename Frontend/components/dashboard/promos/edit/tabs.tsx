"use client";

import { useRef, type ChangeEvent } from "react";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
import TimeInput from "@/components/ui/TimeInput";
import { DateField } from "@/components/dashboard/content/EditorControls";
import { CHANNELS, CHANNEL_ORDER, type ChannelId } from "@/lib/channels";
import { fmtPeriod } from "@/lib/dashboard/date";
import {
  PROMO_TYPE,
  PROMO_TYPE_ORDER,
  fmtNum,
  promoConversion,
  promoCtr,
  promoProgress,
  type Promo,
  type PromoType,
} from "@/lib/dashboard/promos";
import { Card, ChoiceCards, TextAreaField, TextField } from "./fields";
import type { PromoDraft } from "./draft";

export type AiKey =
  | "title" | "description" | "discount" | "code"
  | "headline" | "subheadline" | "body" | "banner";

export interface TabProps {
  draft: PromoDraft;
  set: <K extends keyof PromoDraft>(key: K, value: PromoDraft[K]) => void;
  aiBusy: AiKey | null;
  runAi: (key: AiKey) => void;
}

const aiProps = (key: AiKey, busy: AiKey | null, run: (k: AiKey) => void, labels?: { empty?: string; filled?: string }) => ({
  loading: busy === key,
  onClick: () => run(key),
  labelEmpty: labels?.empty,
  labelFilled: labels?.filled,
});

/* ══ Информация ══ */
export function InfoTab({ draft, set, aiBusy, runAi }: TabProps) {
  return (
    <div className="flex flex-col gap-4">
      <Card title="Об акции" hint="Название и описание видят гости — их же использует ИИ для постов">
        <div className="flex flex-col gap-4">
          <TextField
            label="Название"
            value={draft.title}
            onChange={(v) => set("title", v)}
            placeholder="Например: Счастливые часы"
            ai={aiProps("title", aiBusy, runAi, { filled: "Улучшить" })}
          />
          <TextAreaField
            label="Описание"
            value={draft.description}
            onChange={(v) => set("description", v)}
            placeholder="Что получает гость и на каких условиях"
            ai={aiProps("description", aiBusy, runAi)}
          />
        </div>
      </Card>

      <Card title="Когда действует">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">Начало</span>
            <DateField value={draft.dateFrom} onChange={(v) => set("dateFrom", v)} variant="field" ariaLabel="Дата начала акции" />
          </div>
          <div>
            <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">Окончание</span>
            <DateField value={draft.dateTo} onChange={(v) => set("dateTo", v)} variant="field" ariaLabel="Дата окончания акции" />
          </div>
          <div>
            <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">Время старта</span>
            <TimeInput value={draft.timeStart} onChange={(v) => set("timeStart", v)} variant="field" ariaLabel="Время старта акции" />
          </div>
          <div className="sm:col-span-3">
            <TextField
              label="Цель по использованиям"
              value={draft.goal}
              onChange={(v) => set("goal", v.replace(/\D/g, ""))}
              placeholder="300"
              inputMode="numeric"
              hint="Прогресс к цели видно в карточке акции"
            />
          </div>
        </div>
      </Card>
    </div>
  );
}

/* ══ Механика: тип, оффер и промокод живут только здесь ══ */
export function MechanicsTab({ draft, set, aiBusy, runAi }: TabProps) {
  const t = PROMO_TYPE[draft.type];

  return (
    <div className="flex flex-col gap-4">
      <Card title="Механика" hint="Тип определяет, какие условия нужно заполнить">
        <ChoiceCards
          ariaLabel="Механика акции"
          value={draft.type}
          onChange={(v: PromoType) => set("type", v)}
          options={PROMO_TYPE_ORDER.map((tp) => ({
            id: tp,
            label: PROMO_TYPE[tp].label,
            icon: PROMO_TYPE[tp].icon,
            hint: PROMO_TYPE[tp].hint || undefined,
          }))}
        />
      </Card>

      <Card title={`Условия · ${t.label}`}>
        <div key={draft.type} className="uc-tab-in grid grid-cols-1 gap-4 sm:grid-cols-2">
          <TextField
            label={draft.type === "gift" ? "Оффер" : "Размер выгоды"}
            value={draft.discount}
            onChange={(v) => set("discount", v)}
            placeholder={t.hint || "−20%"}
            ai={aiProps("discount", aiBusy, runAi, { empty: "Подобрать", filled: "Подобрать" })}
          />

          {draft.type === "discount" && (
            <TextField label="Минимальная сумма" value={draft.minOrder} onChange={(v) => set("minOrder", v.replace(/\D/g, ""))} placeholder="Без ограничений" inputMode="numeric" />
          )}

          {draft.type === "gift" && (
            <>
              <TextField label="Какой подарок" value={draft.giftItem} onChange={(v) => set("giftItem", v)} placeholder="Второй напиток" />
              <div className="sm:col-span-2">
                <TextField label="Условия получения" value={draft.giftCondition} onChange={(v) => set("giftCondition", v)} placeholder="При покупке любого напитка" />
              </div>
            </>
          )}

          {draft.type === "event" && (
            <>
              <TextField label="Место проведения" value={draft.eventPlace} onChange={(v) => set("eventPlace", v)} placeholder="Кофейня на Немиге" />
              <div className="sm:col-span-2">
                <TextField label="Что будет на событии" value={draft.giftCondition} onChange={(v) => set("giftCondition", v)} placeholder="Праздничное меню и розыгрыш сертификатов" />
              </div>
            </>
          )}

          {draft.type === "code" && (
            <TextField label="Лимит активаций" value={draft.codeLimit} onChange={(v) => set("codeLimit", v.replace(/\D/g, ""))} placeholder="400" inputMode="numeric" />
          )}
        </div>
      </Card>

      {/* Промокод — один блок: переключатель и поле под ним */}
      <Card
        title="Промокод"
        hint={draft.hasCode ? "Гость называет код на кассе или вводит при заказе" : "Акция работает без кода"}
        action={
          <button
            type="button"
            onClick={() => set("hasCode", !draft.hasCode)}
            role="switch"
            aria-checked={draft.hasCode}
            aria-label="Использовать промокод"
            className={`relative h-5 w-9 shrink-0 rounded-full transition duration-200 ${draft.hasCode ? "bg-brand" : "bg-border"}`}
          >
            <span
              className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-all duration-200 ${draft.hasCode ? "left-4.5" : "left-0.5"}`}
            />
          </button>
        }
      >
        {draft.hasCode && (
          <div className="uc-tab-in sm:max-w-xs">
            <TextField
              label="Код"
              value={draft.code}
              onChange={(v) => set("code", v.toUpperCase())}
              placeholder="HAPPY20"
              mono
              ai={aiProps("code", aiBusy, runAi, { empty: "Подобрать", filled: "Подобрать" })}
            />
          </div>
        )}
      </Card>
    </div>
  );
}

/* ══ Контент ══ */
export function ContentTab({ draft, set, aiBusy, runAi }: TabProps) {
  const fileInput = useRef<HTMLInputElement>(null);
  const urls = useRef<string[]>([]);

  const onFile = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      const u = URL.createObjectURL(f);
      urls.current.push(u);
      set("image", u);
    }
    e.target.value = "";
  };

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_20rem]">
      <div className="flex flex-col gap-4">
        <Card title="Баннер">
          <div className="relative aspect-[16/9] w-full overflow-hidden rounded-2xl bg-surface-soft">
            {draft.image ? (
              <Image
                key={draft.image}
                src={draft.image}
                alt=""
                fill
                sizes="(max-width: 1280px) 100vw, 640px"
                unoptimized={draft.image.startsWith("blob:")}
                className="uc-fade-in object-cover"
              />
            ) : (
              <button
                type="button"
                onClick={() => fileInput.current?.click()}
                className="absolute inset-0 grid place-items-center text-ink-muted transition duration-200 hover:text-ink"
              >
                <span className="inline-flex items-center gap-2 text-sm">
                  <Icon name="image-plus" size={18} aria-hidden="true" /> Добавить изображение
                </span>
              </button>
            )}
            {aiBusy === "banner" && (
              <div className="absolute inset-0 grid place-items-center bg-ink/45 backdrop-blur-sm">
                <span className="inline-flex items-center gap-2 text-sm font-medium text-white">
                  <Icon name="sparkles" size={16} className="animate-pulse" aria-hidden="true" /> Генерирую…
                </span>
              </div>
            )}
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-1">
            <button type="button" onClick={() => fileInput.current?.click()} className="rounded-lg px-2.5 py-1.5 text-xs font-medium text-ink-muted transition duration-150 hover:bg-surface-soft hover:text-ink">
              Заменить
            </button>
            <button type="button" onClick={() => runAi("banner")} className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-brand transition duration-150 hover:bg-brand/10">
              <Icon name="sparkles" size={12} aria-hidden="true" /> Сгенерировать ИИ
            </button>
            <button type="button" onClick={() => fileInput.current?.click()} className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium text-ink-muted transition duration-150 hover:bg-surface-soft hover:text-ink">
              <Icon name="crop" size={12} aria-hidden="true" /> Обрезать
            </button>
            {draft.image && (
              <button type="button" onClick={() => set("image", undefined)} className="rounded-lg px-2.5 py-1.5 text-xs font-medium text-ink-muted transition duration-150 hover:bg-surface-soft hover:text-[#e5484d]">
                Удалить
              </button>
            )}
          </div>
          <input ref={fileInput} type="file" accept="image/*" hidden onChange={onFile} />
        </Card>

        <Card
          title="Тексты"
          action={
            <button
              type="button"
              onClick={() => runAi("body")}
              disabled={aiBusy === "body"}
              className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-brand/30 bg-brand/5 px-3 py-1.5 text-xs font-semibold text-brand transition duration-200 hover:bg-brand/10 disabled:opacity-50"
            >
              {aiBusy === "body" ? (
                <><Icon name="refresh" size={12} className="animate-spin" aria-hidden="true" /> Генерирую…</>
              ) : (
                <><Icon name="sparkles" size={12} aria-hidden="true" /> Написать анонс</>
              )}
            </button>
          }
        >
          <div className="flex flex-col gap-4">
            <TextField label="Заголовок на баннере" value={draft.headline} onChange={(v) => set("headline", v)} placeholder="Счастливые часы" ai={aiProps("headline", aiBusy, runAi, { filled: "Улучшить" })} />
            <TextField label="Подзаголовок на баннере" value={draft.subheadline} onChange={(v) => set("subheadline", v)} placeholder="−20% на всё меню" ai={aiProps("subheadline", aiBusy, runAi, { filled: "Улучшить" })} />
            <TextAreaField label="Дополнительный текст" value={draft.bodyText} onChange={(v) => set("bodyText", v)} rows={4} placeholder="Расскажите про условия и повод зайти" />
          </div>
        </Card>
      </div>

      {/* Предпросмотр: пока одна сеть — ВКонтакте */}
      <div className="xl:sticky xl:top-4 xl:h-fit">
        <Card title="Предпросмотр">
          <div className="overflow-hidden rounded-2xl border border-border/70 bg-card">
            <div className="flex items-center gap-2 px-3 py-2.5">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand/15 text-xs font-bold text-brand">
                {(draft.headline || "U").slice(0, 1)}
              </span>
              <span className="min-w-0">
                <span className="block truncate text-xs font-semibold text-ink">{draft.headline || "Ваш бизнес"}</span>
                <span className="block text-[0.6875rem] text-ink-muted">{fmtPeriod(draft.dateFrom, draft.dateTo)}</span>
              </span>
            </div>

            {draft.image && (
              <div className="relative aspect-[4/3] w-full">
                <Image src={draft.image} alt="" fill sizes="320px" unoptimized={draft.image.startsWith("blob:")} className="object-cover" />
                {draft.discount && (
                  <span className="absolute bottom-2 right-3 font-display text-2xl font-black text-white drop-shadow-lg">{draft.discount}</span>
                )}
              </div>
            )}

            <div className="flex flex-col gap-1.5 px-3 py-3">
              <p className="text-sm font-semibold text-ink">{draft.subheadline || draft.title}</p>
              <p className="text-xs leading-relaxed text-ink-muted">{draft.bodyText || draft.description}</p>
              {draft.hasCode && draft.code && (
                <span className="mt-1 w-fit rounded-lg border border-border bg-surface-soft px-2.5 py-1 font-mono text-[0.6875rem] font-bold tracking-widest text-ink">
                  {draft.code}
                </span>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

/* ══ Публикация ══ */
export function PublishTab({
  draft,
  set,
  onPublish,
  onSchedule,
}: TabProps & { onPublish: () => void; onSchedule: () => void }) {
  const toggle = (id: ChannelId) =>
    set("channels", draft.channels.includes(id) ? draft.channels.filter((c) => c !== id) : [...draft.channels, id]);

  return (
    <div className="flex flex-col gap-4">
      <Card title="Каналы" hint="Публикация адаптируется под каждую площадку автоматически">
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {CHANNEL_ORDER.map((id) => {
            const ch = CHANNELS[id];
            const on = draft.channels.includes(id);
            return (
              <button
                key={id}
                type="button"
                onClick={() => toggle(id)}
                aria-pressed={on}
                className={`flex items-center gap-2.5 rounded-2xl border p-3 text-left transition duration-200 ${
                  on ? "border-brand bg-brand/8" : "border-border/70 hover:border-brand/30"
                }`}
              >
                {ch.icon && ch.iconType !== "wordmark" ? (
                  <Image src={ch.icon} alt="" width={18} height={18} className="h-[1.125rem] w-[1.125rem] object-contain" aria-hidden="true" />
                ) : (
                  <span className="h-4 w-4 rounded-full" style={{ backgroundColor: ch.colorVar }} aria-hidden="true" />
                )}
                <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{ch.label}</span>
                <span className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition duration-200 ${on ? "border-brand bg-brand text-white" : "border-border"}`}>
                  {on && <Icon name="check" size={12} aria-hidden="true" />}
                </span>
              </button>
            );
          })}
        </div>
      </Card>

      <Card title="Дата публикации">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">Дата</span>
            <DateField value={draft.publishDate} onChange={(v) => set("publishDate", v)} variant="field" ariaLabel="Дата публикации акции" />
          </div>
          <div>
            <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">Время</span>
            <TimeInput value={draft.publishTime} onChange={(v) => set("publishTime", v)} variant="field" ariaLabel="Время публикации акции" />
          </div>
        </div>

        <div className="mt-5 flex flex-col gap-2 sm:flex-row">
          <button type="button" onClick={onSchedule} disabled={draft.channels.length === 0} className="btn-glass inline-flex items-center justify-center gap-2 px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50">
            <Icon name="calendar-plus" size={16} aria-hidden="true" /> Запланировать
          </button>
          <button type="button" onClick={onPublish} disabled={draft.channels.length === 0} className="btn-glass-blue inline-flex items-center justify-center gap-2 px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50">
            <Icon name="send" size={16} aria-hidden="true" /> Опубликовать сейчас
          </button>
        </div>
      </Card>
    </div>
  );
}

/* ══ Статистика ══ */
function StatTile({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-[20px] border border-border/70 bg-card/70 px-5 py-4">
      <p className="text-xs font-medium text-ink-muted">{label}</p>
      <p className="mt-1.5 font-display text-2xl font-extrabold tabular-nums text-ink">{value}</p>
      {hint && <p className="mt-1 text-xs text-ink-muted">{hint}</p>}
    </div>
  );
}

export function StatsTab({ promo, draft }: { promo: Promo; draft: PromoDraft }) {
  const s = promo.stats;
  const ctr = promoCtr(s);
  const conv = promoConversion(promo);
  const pct = promoProgress(promo);
  const daily = s?.daily ?? [];
  const max = Math.max(1, ...daily);

  if (!s) {
    return (
      <Card>
        <div className="flex flex-col items-center gap-3 py-10 text-center">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-soft text-ink-muted">
            <Icon name="bar-chart" size={22} aria-hidden="true" />
          </span>
          <p className="text-sm font-semibold text-ink">Статистика появится после запуска</p>
          <p className="max-w-sm text-sm text-ink-muted">
            Как только акция стартует — здесь будут показы, переходы и использования по дням.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile label="Использования" value={fmtNum(promo.uses ?? 0)} hint={pct !== null ? `${pct}% от цели` : undefined} />
        <StatTile label="Просмотры" value={fmtNum(s.views)} />
        <StatTile label="Переходы" value={fmtNum(s.clicks)} />
        <StatTile label="CTR" value={ctr !== null ? `${ctr}%` : "—"} hint={conv !== null ? `Конверсия ${conv}%` : undefined} />
      </div>

      <Card title="Использования по дням" hint={fmtPeriod(draft.dateFrom, draft.dateTo)}>
        <div className="flex h-44 items-stretch gap-2">
          {daily.map((v, i) => (
            <div key={i} className="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-1.5">
              <span className="text-[0.6875rem] tabular-nums text-ink-muted">{v}</span>
              <div
                className="uc-bar-rise w-full rounded-t-lg bg-gradient-to-t from-brand/40 to-brand"
                style={{ height: `${Math.max(6, (v / max) * 100)}%`, animationDelay: `${i * 40}ms` }}
              />
              <span className="text-[0.6875rem] text-ink-muted">{i + 1}д</span>
            </div>
          ))}
        </div>
      </Card>

      <Card title="Каналы">
        <ul className="flex flex-col gap-2.5">
          {draft.channels.map((id, i) => {
            const ch = CHANNELS[id];
            const share = Math.round((s.clicks / draft.channels.length) * (1 - i * 0.15));
            return (
              <li key={id} className="flex items-center gap-3">
                {ch.icon && ch.iconType !== "wordmark" ? (
                  <Image src={ch.icon} alt="" width={18} height={18} className="h-[1.125rem] w-[1.125rem] shrink-0 object-contain" aria-hidden="true" />
                ) : (
                  <span className="h-4 w-4 shrink-0 rounded-full" style={{ backgroundColor: ch.colorVar }} aria-hidden="true" />
                )}
                <span className="w-24 shrink-0 truncate text-sm text-ink">{ch.label}</span>
                <span className="h-1.5 min-w-0 flex-1 overflow-hidden rounded-full bg-border/70">
                  <span
                    className="uc-bar-fill block h-full rounded-full bg-brand"
                    style={{ width: `${Math.max(8, 100 - i * 22)}%` }}
                  />
                </span>
                <span className="w-16 shrink-0 text-right text-sm tabular-nums text-ink-muted">{fmtNum(share)}</span>
              </li>
            );
          })}
        </ul>
      </Card>
    </div>
  );
}
