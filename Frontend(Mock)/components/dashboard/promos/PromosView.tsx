"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";
import { CHANNELS, CHANNEL_ORDER, type ChannelId } from "@/lib/channels";
import { toast } from "@/lib/toast";
import { useDashboard } from "@/components/dashboard/DashboardProvider";
import { menuSurfaceClass } from "@/lib/dashboard/surface";
import {
  PROMOS,
  PROMO_STATUS_LABEL,
  PROMO_TYPE,
  PROMO_TYPE_ORDER,
  fmtNum,
  promoCounts,
  promoProgress,
  promoTotalUses,
  type Promo,
  type PromoStatus,
  type PromoType,
} from "@/lib/dashboard/promos";
import { FilterSelect, KpiTile, PageHeader, SearchInput, Segmented, useDismiss } from "./ui";

type StatusFilter = "all" | PromoStatus;
type TypeFilter = "all" | PromoType;
type ChannelFilter = "all" | ChannelId;
type SortKey = "recent" | "uses" | "title" | "ending";
type ViewMode = "grid" | "list";
type CardAction = "duplicate" | "finish" | "resume" | "delete";

const PROGRESS_COLOR: Record<PromoStatus, string> = {
  active: "bg-success",
  scheduled: "bg-brand",
  finished: "bg-ink-muted",
};

const STATUS_DOT: Record<PromoStatus, string> = {
  active: "bg-success",
  scheduled: "bg-brand",
  finished: "bg-ink-muted",
};

const SORTS: { id: SortKey; label: string }[] = [
  { id: "recent", label: "Сначала новые" },
  { id: "uses", label: "По использованиям" },
  { id: "title", label: "По названию" },
  { id: "ending", label: "Скоро завершатся" },
];

/* ── Меню «ещё» на карточке ── */
function MoreMenu({
  promo,
  onAction,
  variant = "plain",
}: {
  promo: Promo;
  onAction: (a: CardAction) => void;
  /** overlay — кнопка поверх обложки, plain — на светлой поверхности. */
  variant?: "plain" | "overlay";
}) {
  const { surfaceStyle } = useDashboard();
  const [open, setOpen] = useState(false);
  const ref = useDismiss<HTMLDivElement>(open, () => setOpen(false));
  const finished = promo.status === "finished";

  const items: { id: CardAction; label: string; icon: IconName; danger?: boolean }[] = [
    finished
      ? { id: "resume", label: "Возобновить", icon: "play" }
      : { id: "finish", label: "Завершить", icon: "check" },
    { id: "delete", label: "Удалить", icon: "trash", danger: true },
  ];

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label={`Ещё действия с акцией «${promo.title}»`}
        aria-expanded={open}
        className={
          variant === "overlay"
            ? "flex h-8 w-8 items-center justify-center rounded-full border border-white/15 bg-black/45 text-white backdrop-blur-md transition duration-200 hover:bg-black/65"
            : "flex h-8 w-8 items-center justify-center rounded-full text-ink-muted transition duration-200 hover:bg-surface-soft hover:text-ink"
        }
      >
        <Icon name="menu" size={15} aria-hidden="true" />
      </button>
      {open && (
        <div
          className={`uc-pop-in absolute right-0 top-full z-30 mt-1.5 w-44 overflow-hidden rounded-2xl border border-border/70 p-1.5 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}
        >
          {items.map((it) => (
            <button
              key={it.id}
              type="button"
              onClick={() => { setOpen(false); onAction(it.id); }}
              className={`flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-left text-sm transition duration-150 hover:bg-surface-soft ${
                it.danger ? "text-[#e5484d]" : "text-ink"
              }`}
            >
              <Icon name={it.icon} size={14} aria-hidden="true" /> {it.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function Channels({ ids, size = 15 }: { ids: ChannelId[]; size?: number }) {
  return (
    <span className="flex shrink-0 items-center gap-1">
      {ids.map((id) => {
        const ch = CHANNELS[id];
        return ch?.icon && ch.iconType !== "wordmark" ? (
          <Image
            key={id}
            src={ch.icon}
            alt={ch.label}
            width={size}
            height={size}
            style={{ width: size, height: size }}
            className="object-contain"
          />
        ) : null;
      })}
    </span>
  );
}

function Progress({ p }: { p: Promo }) {
  const pct = promoProgress(p);
  if (pct === null) return null;
  return (
    <div>
      <div className="flex items-baseline justify-between gap-2">
        <span className="font-display text-base font-bold tabular-nums text-ink">
          {fmtNum(p.uses ?? 0)} <span className="text-sm font-medium text-ink-muted">/ {fmtNum(p.goal ?? 0)}</span>
        </span>
        <span className="text-xs font-semibold tabular-nums text-ink-muted">{pct}%</span>
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-border/70">
        <div
          className={`uc-bar-fill h-full rounded-full ${PROGRESS_COLOR[p.status]}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

/* ── Карточка акции: вся карточка — ссылка в редактирование ── */
function PromoCard({ p }: { p: Promo }) {
  const t = PROMO_TYPE[p.type];
  return (
    <Link
      href={`/dashboard/promos/${p.id}`}
      className={`group relative flex flex-col overflow-hidden rounded-[20px] border border-border/70 bg-card/80 outline-none transition duration-200 hover:-translate-y-1 hover:border-brand/40 hover:shadow-lift focus-visible:ring-2 focus-visible:ring-brand/50 ${
        p.status === "finished" ? "opacity-75 hover:opacity-100" : ""
      }`}
    >
      <div className="relative h-40 shrink-0 overflow-hidden">
        {p.image ? (
          <>
            <Image
              src={p.image}
              alt=""
              fill
              sizes="(max-width: 1024px) 100vw, 33vw"
              className="object-cover transition-transform duration-300 group-hover:scale-[1.03]"
              unoptimized={p.image.startsWith("blob:")}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-black/25" />
          </>
        ) : (
          <div className={`absolute inset-0 grid place-items-center bg-surface-soft bg-gradient-to-br ${t.cover}`}>
            <Icon name={t.icon} size={56} className="opacity-25" aria-hidden="true" />
          </div>
        )}

        <span
          className={`absolute left-3 top-3 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[0.6875rem] font-semibold backdrop-blur-md ${
            p.image ? "border border-white/15 bg-black/55 text-white" : t.chip
          }`}
        >
          <Icon name={t.icon} size={11} aria-hidden="true" /> {t.label}
        </span>

        <span
          className={`absolute right-3 top-3 inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[0.6875rem] font-medium backdrop-blur-md ${
            p.image ? "border border-white/15 bg-black/55 text-white" : "border border-border bg-card/80 text-ink"
          }`}
        >
          <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[p.status]}`} aria-hidden="true" />
          {PROMO_STATUS_LABEL[p.status]}
        </span>

        {p.discount && (
          <span className="absolute bottom-3 right-4 font-display text-3xl font-black leading-none text-white drop-shadow-lg">
            {p.discount}
          </span>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-4 p-5">
        <div className="min-w-0">
          <h3 className="truncate font-display text-lg font-bold leading-snug text-ink">{p.title}</h3>
          <p className="mt-1 truncate text-sm text-ink-muted">{p.description}</p>
        </div>

        <div className="mt-auto flex flex-col gap-4">
          <Progress p={p} />
          <div className="flex items-center justify-between gap-2">
            <span className="min-w-0 truncate text-xs text-ink-muted">{p.period}</span>
            <Channels ids={p.channels} />
          </div>
        </div>
      </div>
    </Link>
  );
}

/* ── Строка списка: то же самое, но плотнее ── */
function PromoRow({ p, onAction }: { p: Promo; onAction: (a: CardAction) => void }) {
  const t = PROMO_TYPE[p.type];
  const pct = promoProgress(p);

  return (
    <article className="group relative flex items-center gap-4 rounded-[20px] border border-border/70 bg-card/80 p-3 transition duration-200 hover:border-brand/40 hover:shadow-soft">
      <Link
        href={`/dashboard/promos/${p.id}`}
        className="flex min-w-0 flex-1 items-center gap-4 outline-none focus-visible:ring-2 focus-visible:ring-brand/50"
      >
        <span className="relative h-14 w-20 shrink-0 overflow-hidden rounded-2xl">
          {p.image ? (
            <Image src={p.image} alt="" fill sizes="80px" className="object-cover" unoptimized={p.image.startsWith("blob:")} />
          ) : (
            <span className={`absolute inset-0 grid place-items-center bg-surface-soft bg-gradient-to-br ${t.cover}`}>
              <Icon name={t.icon} size={20} className="opacity-40" aria-hidden="true" />
            </span>
          )}
        </span>

        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-2">
            <span className="truncate font-semibold text-ink">{p.title}</span>
            <span className={`hidden shrink-0 rounded-full px-2 py-0.5 text-[0.6875rem] font-semibold sm:inline ${t.chip}`}>
              {t.label}
            </span>
          </span>
          <span className="mt-0.5 flex items-center gap-2 text-xs text-ink-muted">
            <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${STATUS_DOT[p.status]}`} aria-hidden="true" />
            {PROMO_STATUS_LABEL[p.status]} · {p.period}
          </span>
        </span>

        <span className="hidden w-40 shrink-0 md:block">
          {pct !== null ? (
            <>
              <span className="flex items-baseline justify-between gap-2 text-xs">
                <span className="font-semibold tabular-nums text-ink">
                  {fmtNum(p.uses ?? 0)} / {fmtNum(p.goal ?? 0)}
                </span>
                <span className="tabular-nums text-ink-muted">{pct}%</span>
              </span>
              <span className="mt-1.5 block h-1.5 overflow-hidden rounded-full bg-border/70">
                <span className={`uc-bar-fill block h-full rounded-full ${PROGRESS_COLOR[p.status]}`} style={{ width: `${pct}%` }} />
              </span>
            </>
          ) : (
            <span className="text-xs text-ink-muted">Цель не задана</span>
          )}
        </span>

        <span className="hidden shrink-0 lg:flex">
          <Channels ids={p.channels} />
        </span>
      </Link>

      <div className="flex shrink-0 items-center gap-1">
        <Link
          href={`/dashboard/promos/${p.id}`}
          aria-label={`Редактировать «${p.title}»`}
          className="flex h-8 w-8 items-center justify-center rounded-full text-ink-muted transition duration-200 hover:bg-surface-soft hover:text-ink"
        >
          <Icon name="edit" size={15} aria-hidden="true" />
        </Link>
        <Link
          href={`/dashboard/promos/${p.id}?tab=stats`}
          aria-label={`Статистика «${p.title}»`}
          className="hidden h-8 w-8 items-center justify-center rounded-full text-ink-muted transition duration-200 hover:bg-surface-soft hover:text-ink sm:flex"
        >
          <Icon name="bar-chart" size={15} aria-hidden="true" />
        </Link>
        <button
          type="button"
          onClick={() => onAction("duplicate")}
          aria-label={`Дублировать «${p.title}»`}
          className="hidden h-8 w-8 items-center justify-center rounded-full text-ink-muted transition duration-200 hover:bg-surface-soft hover:text-ink sm:flex"
        >
          <Icon name="copy" size={15} aria-hidden="true" />
        </button>
        <MoreMenu promo={p} onAction={onAction} />
      </div>
    </article>
  );
}

/** Вход в создание — такая же карточка, не пустой пунктирный слот. */
function NewPromoCard({ mode }: { mode: ViewMode }) {
  if (mode === "list") {
    return (
      <Link
        href="/dashboard/promos/create"
        className="group flex items-center gap-4 rounded-[20px] border border-brand/25 bg-brand/[0.06] p-4 transition duration-200 hover:border-brand/50 hover:bg-brand/10"
      >
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-brand/15 text-brand transition duration-200 group-hover:scale-105">
          <Icon name="plus" size={20} aria-hidden="true" />
        </span>
        <span className="min-w-0">
          <span className="block font-semibold text-ink">Создать акцию</span>
          <span className="block truncate text-sm text-ink-muted">
            Опишите идею — ИИ подготовит оффер, описание и промокод
          </span>
        </span>
      </Link>
    );
  }

  return (
    <Link
      href="/dashboard/promos/create"
      className="group flex flex-col justify-between gap-6 rounded-[20px] border border-brand/25 bg-gradient-to-br from-brand/12 via-brand/[0.06] to-transparent p-6 transition duration-200 hover:-translate-y-1 hover:border-brand/50 hover:shadow-lift"
    >
      <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand/15 text-brand transition duration-200 group-hover:scale-105">
        <Icon name="plus" size={22} aria-hidden="true" />
      </span>
      <span>
        <span className="block font-display text-lg font-bold text-ink">Создать акцию</span>
        <span className="mt-1.5 block text-sm leading-relaxed text-ink-muted">
          Опишите идею — ИИ подготовит оффер, описание и промокод.
        </span>
      </span>
      <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand">
        <Icon name="sparkles" size={15} aria-hidden="true" /> Начать
      </span>
    </Link>
  );
}

function EmptyResult({ onReset }: { onReset: () => void }) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-[20px] border border-dashed border-border bg-card/40 px-6 py-14 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-soft text-ink-muted">
        <Icon name="search" size={22} aria-hidden="true" />
      </span>
      <p className="text-sm font-semibold text-ink">Ничего не нашлось</p>
      <button type="button" onClick={onReset} className="text-sm font-medium text-brand transition hover:opacity-70">
        Сбросить фильтры
      </button>
    </div>
  );
}

export default function PromosView() {
  const router = useRouter();
  const [list, setList] = useState<Promo[]>(PROMOS);

  const [status, setStatus] = useState<StatusFilter>("all");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortKey>("recent");
  const [type, setType] = useState<TypeFilter>("all");
  const [channel, setChannel] = useState<ChannelFilter>("all");
  const [mode, setMode] = useState<ViewMode>("grid");

  const counts = promoCounts(list);
  const totalUses = promoTotalUses(list);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    const filtered = list.filter((p) => {
      if (status !== "all" && p.status !== status) return false;
      if (type !== "all" && p.type !== type) return false;
      if (channel !== "all" && !p.channels.includes(channel)) return false;
      if (q && !`${p.title} ${p.description} ${p.code ?? ""}`.toLowerCase().includes(q)) return false;
      return true;
    });

    const order: Record<PromoStatus, number> = { active: 0, scheduled: 1, finished: 2 };
    return [...filtered].sort((a, b) => {
      switch (sort) {
        case "uses": return (b.uses ?? 0) - (a.uses ?? 0);
        case "title": return a.title.localeCompare(b.title, "ru");
        case "ending": return order[a.status] - order[b.status] || a.period.localeCompare(b.period, "ru");
        default: return order[a.status] - order[b.status];
      }
    });
  }, [list, status, type, channel, query, sort]);

  const resetFilters = () => {
    setStatus("all");
    setQuery("");
    setType("all");
    setChannel("all");
  };

  const act = (p: Promo, action: CardAction) => {
    if (action === "delete") {
      setList((cur) => cur.filter((x) => x.id !== p.id));
      toast(`Акция «${p.title}» удалена`);
      return;
    }
    if (action === "duplicate") {
      const copy: Promo = {
        ...p,
        id: `${p.id}-copy-${list.length}`,
        title: `${p.title} — копия`,
        status: "scheduled",
        uses: undefined,
        metricValue: "—",
      };
      setList((cur) => {
        const i = cur.findIndex((x) => x.id === p.id);
        return [...cur.slice(0, i + 1), copy, ...cur.slice(i + 1)];
      });
      toast("Копия создана — отредактируйте и запустите");
      return;
    }
    const next: PromoStatus = action === "finish" ? "finished" : "active";
    setList((cur) => cur.map((x) => (x.id === p.id ? { ...x, status: next } : x)));
    toast(action === "finish" ? "Акция завершена" : "Акция снова активна");
  };

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="Акции"
        subtitle="Создавайте акции, спецпредложения и события"
        action={
          <button
            type="button"
            onClick={() => router.push("/dashboard/promos/create")}
            className="btn-glass-blue inline-flex shrink-0 items-center gap-2 self-start px-4 py-2.5 text-sm font-semibold"
          >
            <Icon name="plus" size={16} aria-hidden="true" /> Создать акцию
          </button>
        }
      />

      {/* KPI: плитки статусов работают фильтром — повторный клик снимает его */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <KpiTile
          label="Активные"
          value={String(counts.active)}
          delta="↑12%"
          tone="success"
          active={status === "active"}
          onClick={() => setStatus(status === "active" ? "all" : "active")}
        />
        <KpiTile
          label="Запланированные"
          value={String(counts.scheduled)}
          tone="brand"
          active={status === "scheduled"}
          onClick={() => setStatus(status === "scheduled" ? "all" : "scheduled")}
        />
        <KpiTile
          label="Завершённые"
          value={String(counts.finished)}
          active={status === "finished"}
          onClick={() => setStatus(status === "finished" ? "all" : "finished")}
        />
        <KpiTile label="Всего использований" value={fmtNum(totalUses)} />
      </div>

      {/* Фильтры */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between gap-3 overflow-x-auto">
          <Segmented
            ariaLabel="Фильтр по статусу"
            value={status}
            onChange={setStatus}
            options={[
              { id: "all", label: "Все", count: list.length },
              { id: "active", label: "Активные", count: counts.active },
              { id: "scheduled", label: "Запланированные", count: counts.scheduled },
              { id: "finished", label: "Завершённые", count: counts.finished },
            ]}
          />
          <Segmented
            ariaLabel="Вид отображения"
            compact
            value={mode}
            onChange={setMode}
            options={[
              { id: "grid", icon: "grid", title: "Сетка" },
              { id: "list", icon: "list", title: "Список" },
            ]}
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <SearchInput value={query} onChange={setQuery} placeholder="Поиск по акциям" />
          <FilterSelect
            ariaLabel="Сортировка"
            icon="sort"
            value={sort}
            onChange={setSort}
            options={SORTS}
          />
          <FilterSelect
            ariaLabel="Тип акции"
            value={type}
            onChange={setType}
            options={[
              { id: "all", label: "Все типы" },
              ...PROMO_TYPE_ORDER.map((t) => ({ id: t, label: PROMO_TYPE[t].label, icon: PROMO_TYPE[t].icon })),
            ]}
          />
          <FilterSelect
            ariaLabel="Канал"
            value={channel}
            onChange={setChannel}
            options={[
              { id: "all", label: "Все каналы" },
              ...CHANNEL_ORDER.map((id) => ({ id, label: CHANNELS[id].label })),
            ]}
          />
        </div>
      </div>

      {visible.length === 0 ? (
        <EmptyResult onReset={resetFilters} />
      ) : mode === "grid" ? (
        <div className="stagger-grid grid grid-cols-1 gap-4 md:grid-cols-2 2xl:grid-cols-3 [&>*]:min-w-0">
          {visible.map((p) => (
            <PromoCard key={p.id} p={p} />
          ))}
          <NewPromoCard mode="grid" />
        </div>
      ) : (
        <div className="stagger-grid flex flex-col gap-2.5">
          {visible.map((p) => (
            <PromoRow key={p.id} p={p} onAction={(a) => act(p, a)} />
          ))}
          <NewPromoCard mode="list" />
        </div>
      )}
    </div>
  );
}
