"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import Icon from "@/components/ui/Icon";
import AnchoredPopover from "@/components/ui/AnchoredPopover";
import type { IconName } from "@/lib/icons/solar";
import { CHANNELS, CHANNEL_ORDER, type ChannelId } from "@/lib/channels";
import type { PostStatus } from "@/lib/dashboard/types";
import {
  DAYS_IN_MONTH,
  MONTH_LABEL,
  STATUS_LABEL,
  WEEKDAYS,
  postsByDay,
  type Post,
  type PostType,
} from "@/lib/dashboard/content";
import { useRouter } from "next/navigation";
import { useDashboard } from "@/components/dashboard/DashboardProvider";
import { menuSurfaceClass } from "@/lib/dashboard/surface";

const DAYS_PER_WEEK = 7;
const MONTH_GEN = "февраля"; // мок-месяц

const STATUS_DOT: Record<PostStatus, string> = {
  published: "bg-success",
  scheduled: "bg-brand",
  draft: "bg-ink-muted",
  none: "bg-transparent",
};

const TYPE: Record<PostType, { icon: IconName; label: string; chip: string; cover: string; bar: string; tint: string }> = {
  post: { icon: "file-text", label: "Публикация", chip: "bg-brand/10 text-brand", cover: "bg-brand/8 text-brand", bar: "bg-brand", tint: "text-brand" },
  promo: { icon: "gift", label: "Акция", chip: "bg-brand-pink/10 text-brand-pink", cover: "bg-brand-pink/8 text-brand-pink", bar: "bg-brand-pink", tint: "text-brand-pink" },
  video: { icon: "clapperboard", label: "Видео", chip: "bg-brand-purple/10 text-brand-purple", cover: "bg-brand-purple/8 text-brand-purple", bar: "bg-brand-purple", tint: "text-brand-purple" },
};

const weekdayOf = (day: number) => WEEKDAYS[(day - 1) % DAYS_PER_WEEK];
const ALL_DAYS = Array.from({ length: DAYS_IN_MONTH }, (_, i) => i + 1);

function ChannelIcons({ post }: { post: Post }) {
  if (post.channels.length === 0) return null;
  return (
    <span className="flex items-center gap-0.5">
      {post.channels.map((id) => {
        const ch = CHANNELS[id];
        return ch.icon && ch.iconType !== "wordmark" ? (
          <Image key={id} src={ch.icon} alt={ch.label} width={14} height={14} className="h-3.5 w-3.5 object-contain" />
        ) : null;
      })}
    </span>
  );
}

function StatusBadge({ status }: { status: PostStatus }) {
  const cls: Record<PostStatus, string> = {
    published: "bg-success/15 text-success",
    scheduled: "bg-brand/12 text-brand",
    draft: "bg-ink-muted/15 text-ink-muted",
    none: "bg-ink-muted/15 text-ink-muted",
  };
  return <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-[0.6875rem] font-medium ${cls[status]}`}>{STATUS_LABEL[status]}</span>;
}

/** Полноразмерная карточка поста: обложка + заголовок + текст-превью + мета.
 *  variant "stack" — всегда вертикально (для узкой панели дня). */
function PostCard({ post, variant = "card", onOpen }: { post: Post; variant?: "card" | "stack"; onOpen: (p: Post) => void }) {
  const { icon, label, cover, bar } = TYPE[post.type];
  const horizontal = variant === "card";

  return (
    <button
      type="button"
      onClick={() => onOpen(post)}
      className={`group relative block w-full overflow-hidden rounded-2xl border border-border bg-card text-left shadow-soft transition hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-lift ${
        horizontal ? "sm:flex" : ""
      }`}
    >
      {/* Цветная метка типа по левому краю карточки */}
      <span className={`pointer-events-none absolute inset-y-0 left-0 z-20 w-1.5 ${bar}`} aria-hidden="true" />
      {/* Обложка */}
      <div
        className={`relative aspect-[16/9] w-full shrink-0 overflow-hidden ${
          horizontal ? "sm:aspect-auto sm:w-48 md:w-56" : ""
        }`}
      >
        {post.image ? (
          <Image
            src={post.image}
            alt=""
            fill
            sizes={horizontal ? "(max-width: 640px) 100vw, 224px" : "384px"}
            className="object-cover transition duration-300 group-hover:scale-[1.03]"
          />
        ) : (
          <div className={`flex h-full w-full items-center justify-center ${cover}`}>
            <Icon name={icon} size={30} aria-hidden="true" />
          </div>
        )}
        {/* Плотная подложка: цветной текст на светлой фотографии не читался */}
        <span className="absolute left-2 top-2 inline-flex items-center gap-1 rounded-full border border-white/15 bg-black/55 px-2 py-0.5 text-[0.6875rem] font-semibold text-white backdrop-blur-sm">
          <Icon name={icon} size={12} aria-hidden="true" /> {label}
        </span>
      </div>

      {/* Текст */}
      <div className="flex min-w-0 flex-1 flex-col p-4">
        <div className="mb-1.5 flex items-center justify-between gap-2">
          <span className="flex items-center gap-2 text-xs text-ink-muted">
            {post.time !== "—" ? post.time : "без времени"}
            <ChannelIcons post={post} />
          </span>
          <StatusBadge status={post.status} />
        </div>
        <h3 className="text-sm font-bold leading-snug text-ink sm:text-base">{post.title}</h3>
        <p className="mt-1 line-clamp-2 text-[0.8125rem] leading-relaxed text-ink-muted">{post.excerpt}</p>
        <span className="mt-2.5 inline-flex items-center gap-1 text-xs font-medium text-brand opacity-0 transition group-hover:opacity-100">
          Открыть <Icon name="chevron-right" size={13} aria-hidden="true" />
        </span>
      </div>
    </button>
  );
}

const VIEWS = [
  { id: "grid", label: "Лента" },
  { id: "list", label: "Список" },
  { id: "calendar", label: "Месяц" },
] as const;

type ViewId = (typeof VIEWS)[number]["id"];

const STATUS_TABS: { id: "all" | PostStatus; label: string }[] = [
  { id: "all", label: "Все" },
  { id: "scheduled", label: "Запланированные" },
  { id: "published", label: "Опубликованные" },
  { id: "draft", label: "Черновики" },
];

const POST_TYPE_ORDER: PostType[] = ["post", "promo", "video"];

/** Карточка поста в сетке контента (обложка + текст + мета + меню). */
function GridCard({ post, onOpen, onDelete }: { post: Post; onOpen: (p: Post) => void; onDelete: (id: string) => void }) {
  const { surfaceStyle } = useDashboard();
  const [menu, setMenu] = useState(false);
  const t = TYPE[post.type];
  const date = `${String(post.day).padStart(2, "0")}.02.2026`;

  return (
    <article className="group relative flex flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-soft transition hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-lift">
      {/* Обложка */}
      <button type="button" onClick={() => onOpen(post)} className="relative block aspect-[16/10] w-full overflow-hidden text-left">
        {post.image ? (
          <Image src={post.image} alt="" fill sizes="(max-width: 640px) 100vw, 380px" className="object-cover transition duration-300 group-hover:scale-[1.03]" />
        ) : (
          <div className={`flex h-full w-full items-center justify-center ${t.cover}`}>
            <span className="inline-flex items-center gap-1.5 text-sm font-semibold opacity-70">
              <Icon name="sparkles" size={16} aria-hidden="true" /> AI-generated
            </span>
          </div>
        )}
      </button>

      {/* Меню «…» */}
      <div className="absolute right-2.5 top-2.5">
        <button
          type="button"
          onClick={() => setMenu((v) => !v)}
          aria-label="Действия"
          className="flex h-8 w-8 items-center justify-center rounded-full bg-card/90 text-ink shadow-soft backdrop-blur-sm transition hover:bg-card"
        >
          <span className="text-lg leading-none">⋯</span>
        </button>
        {menu && (
          <>
            <button type="button" aria-hidden className="fixed inset-0 z-10 cursor-default" onClick={() => setMenu(false)} />
            <div className={`absolute right-0 z-20 mt-1 w-36 overflow-hidden rounded-xl border border-border py-1 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}>
              <button type="button" onClick={() => { setMenu(false); onOpen(post); }} className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-ink transition hover:bg-surface-soft">
                <Icon name="edit" size={14} aria-hidden="true" /> Редактировать
              </button>
              <button type="button" onClick={() => { setMenu(false); onDelete(post.id); }} className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-[#e5484d] transition hover:bg-surface-soft">
                <Icon name="trash" size={14} aria-hidden="true" /> Удалить
              </button>
            </div>
          </>
        )}
      </div>

      {/* Тело */}
      <div className="flex min-w-0 flex-1 flex-col p-4">
        <div className="mb-1 flex items-start justify-between gap-2">
          <h3 className="text-sm font-bold leading-snug text-ink">{post.title}</h3>
          <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${STATUS_DOT[post.status]}`} title={STATUS_LABEL[post.status]} aria-hidden="true" />
        </div>
        <p className="line-clamp-2 flex-1 text-[0.8125rem] leading-relaxed text-ink-muted">{post.excerpt}</p>
        <div className="mt-3 flex items-center justify-between">
          <ChannelIcons post={post} />
          <span className="text-xs text-ink-muted">{date}</span>
        </div>
      </div>
    </article>
  );
}

/** Общий фильтр контента: сети (дропдаун со списком) + статус (чипы). Удобно на мобилке. */
function ContentFilters({
  view,
  onView,
  chans,
  onToggleChan,
  onOnlyChan,
  onAllChans,
  types,
  onToggleType,
  onOnlyType,
  onAllTypes,
  status,
  onStatus,
}: {
  view: ViewId;
  onView: (v: ViewId) => void;
  chans: ChannelId[];
  onToggleChan: (id: ChannelId) => void;
  onOnlyChan: (id: ChannelId) => void;
  onAllChans: () => void;
  types: PostType[];
  onToggleType: (t: PostType) => void;
  onOnlyType: (t: PostType) => void;
  onAllTypes: () => void;
  status: "all" | PostStatus;
  onStatus: (s: "all" | PostStatus) => void;
}) {
  const { surfaceStyle } = useDashboard();
  const [open, setOpen] = useState(false);
  const [openType, setOpenType] = useState(false);
  const [openStatus, setOpenStatus] = useState(false);
  const chanAnchor = useRef<HTMLDivElement>(null);
  const typeAnchor = useRef<HTMLDivElement>(null);
  const statusAnchor = useRef<HTMLDivElement>(null);
  const allSelected = chans.length === CHANNEL_ORDER.length;
  const label = chans.length === 0 ? "Не выбрано" : allSelected ? "Все сети" : `Выбрано: ${chans.length}`;
  const typeLabel =
    types.length === POST_TYPE_ORDER.length ? "Все типы" : types.length === 0 ? "Не выбрано" : `Выбрано: ${types.length}`;

  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-3 shadow-soft sm:flex-row sm:items-center sm:gap-x-3 sm:p-4 lg:gap-x-4">
      {/* Социальные сети — дропдаун со списком */}
      <div className="flex items-center justify-between gap-2 sm:justify-start">
        <span className="shrink-0 text-sm font-semibold text-ink">Социальные сети</span>
        <div ref={chanAnchor} className="relative">
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-expanded={open}
            className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-soft px-3 py-1.5 text-sm text-ink transition hover:border-brand/40"
          >
            {label}
            <Icon name="chevron-down" size={14} className={`transition ${open ? "rotate-180" : ""}`} aria-hidden="true" />
          </button>
          {/* Портал: у карточки фильтров меню упиралось в край экрана */}
          <AnchoredPopover
            anchorRef={chanAnchor}
            open={open}
            onClose={() => setOpen(false)}
            width={240}
            align="left"
            className={`max-h-72 overflow-y-auto rounded-xl border border-border p-1.5 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}
          >
              <div>
                {/* «Все сети» и «только» — чтобы не выключать площадки по одной */}
                <button
                  type="button"
                  onClick={onAllChans}
                  className={`flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm transition hover:bg-surface-soft ${allSelected ? "text-ink" : "text-ink-muted"}`}
                >
                  <span className="min-w-0 flex-1 truncate">Все сети</span>
                  {allSelected && <Icon name="check" size={15} className="shrink-0 text-brand" aria-hidden="true" />}
                </button>
                <div className="my-1 h-px bg-border" />

                {CHANNEL_ORDER.map((id) => {
                  const ch = CHANNELS[id];
                  const on = chans.includes(id);
                  const only = chans.length === 1 && on;
                  return (
                    <div key={id} className="group/row flex items-center gap-1 rounded-lg pr-1 transition hover:bg-surface-soft">
                      <button
                        type="button"
                        onClick={() => onToggleChan(id)}
                        className={`flex min-w-0 flex-1 items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm transition ${on ? "text-ink" : "text-ink-muted"}`}
                      >
                        <span className="min-w-0 flex-1 truncate">{ch.label}</span>
                        {on && <Icon name="check" size={15} className="shrink-0 text-brand" aria-hidden="true" />}
                      </button>
                      <button
                        type="button"
                        onClick={() => onOnlyChan(id)}
                        aria-label={`Показать только ${ch.label}`}
                        className={`shrink-0 rounded-md px-1.5 py-1 text-[0.6875rem] font-semibold transition ${
                          only ? "text-brand" : "text-ink-muted opacity-0 hover:text-ink group-hover/row:opacity-100"
                        }`}
                      >
                        только
                      </button>
                    </div>
                  );
                })}
              </div>
          </AnchoredPopover>
        </div>
      </div>

      <div className="hidden h-6 w-px shrink-0 bg-border sm:block" />

      {/* Тип контента — дропдаун (мультивыбор) */}
      <div className="flex items-center justify-between gap-2 sm:justify-start">
        <span className="shrink-0 text-sm font-semibold text-ink">Тип</span>
        <div ref={typeAnchor} className="relative">
          <button
            type="button"
            onClick={() => setOpenType((v) => !v)}
            aria-expanded={openType}
            className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-soft px-3 py-1.5 text-sm text-ink transition hover:border-brand/40"
          >
            {typeLabel}
            <Icon name="chevron-down" size={14} className={`transition ${openType ? "rotate-180" : ""}`} aria-hidden="true" />
          </button>
          <AnchoredPopover
            anchorRef={typeAnchor}
            open={openType}
            onClose={() => setOpenType(false)}
            width={224}
            align="left"
            className={`overflow-hidden rounded-xl border border-border p-1.5 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}
          >
              <div>
                <button
                  type="button"
                  onClick={onAllTypes}
                  className={`flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm transition hover:bg-surface-soft ${
                    types.length === POST_TYPE_ORDER.length ? "text-ink" : "text-ink-muted"
                  }`}
                >
                  <span className="min-w-0 flex-1 truncate">Все типы</span>
                  {types.length === POST_TYPE_ORDER.length && <Icon name="check" size={15} className="shrink-0 text-brand" aria-hidden="true" />}
                </button>
                <div className="my-1 h-px bg-border" />

                {POST_TYPE_ORDER.map((t) => {
                  const meta = TYPE[t];
                  const on = types.includes(t);
                  const only = types.length === 1 && on;
                  return (
                    <div key={t} className="group/row flex items-center gap-1 rounded-lg pr-1 transition hover:bg-surface-soft">
                      <button
                        type="button"
                        onClick={() => onToggleType(t)}
                        className={`flex min-w-0 flex-1 items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm transition ${on ? "text-ink" : "text-ink-muted"}`}
                      >
                        <Icon name={meta.icon} size={16} className={on ? meta.tint : "opacity-45"} aria-hidden="true" />
                        <span className="min-w-0 flex-1 truncate">{meta.label}</span>
                        {on && <Icon name="check" size={15} className="shrink-0 text-brand" aria-hidden="true" />}
                      </button>
                      <button
                        type="button"
                        onClick={() => onOnlyType(t)}
                        aria-label={`Показать только ${meta.label}`}
                        className={`shrink-0 rounded-md px-1.5 py-1 text-[0.6875rem] font-semibold transition ${
                          only ? "text-brand" : "text-ink-muted opacity-0 hover:text-ink group-hover/row:opacity-100"
                        }`}
                      >
                        только
                      </button>
                    </div>
                  );
                })}
              </div>
          </AnchoredPopover>
        </div>
      </div>

      <div className="hidden h-6 w-px shrink-0 bg-border sm:block" />

      {/* Статус — дропдаун */}
      <div className="flex items-center justify-between gap-2 sm:justify-start">
        <span className="shrink-0 text-sm font-semibold text-ink">Статус</span>
        <div ref={statusAnchor} className="relative">
          <button
            type="button"
            onClick={() => setOpenStatus((v) => !v)}
            aria-expanded={openStatus}
            className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-soft px-3 py-1.5 text-sm text-ink transition hover:border-brand/40"
          >
            {STATUS_TABS.find((s) => s.id === status)?.label ?? "Все"}
            <Icon name="chevron-down" size={14} className={`transition ${openStatus ? "rotate-180" : ""}`} aria-hidden="true" />
          </button>
          <AnchoredPopover
            anchorRef={statusAnchor}
            open={openStatus}
            onClose={() => setOpenStatus(false)}
            width={208}
            align="left"
            className={`overflow-hidden rounded-xl border border-border p-1.5 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}
          >
              <div>
                {STATUS_TABS.map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => { onStatus(s.id); setOpenStatus(false); }}
                    className={`flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm transition hover:bg-surface-soft ${status === s.id ? "text-ink" : "text-ink-muted"}`}
                  >
                    {s.label}
                    {status === s.id && <Icon name="check-bold" size={15} className="ml-auto text-brand" aria-hidden="true" />}
                  </button>
                ))}
              </div>
          </AnchoredPopover>
        </div>
      </div>

      {/* Переключатель вида — справа на ПК (привычнее), сверху на мобилке */}
      <div role="tablist" className="order-first flex shrink-0 gap-1 self-start rounded-full bg-surface-soft p-1 sm:order-none sm:ml-auto">
        {VIEWS.map((v) => (
          <button
            key={v.id}
            type="button"
            role="tab"
            aria-selected={view === v.id}
            onClick={() => onView(v.id)}
            className={`rounded-full px-3.5 py-1.5 text-sm font-medium transition ${
              v.id === "list" ? "hidden sm:block" : ""
            } ${view === v.id ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"}`}
          >
            {v.id === "grid" ? (
              <>
                <span className="hidden sm:inline">Сетка</span>
                <span className="sm:hidden">Лента</span>
              </>
            ) : (
              v.label
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

/** Пустой день — слот «Запланировать». */
function EmptyDayCard({ day }: { day: number }) {
  const date = `${String(day).padStart(2, "0")}.02`;
  return (
    <Link
      href={`/dashboard/create?day=${day}`}
      className="group flex h-full min-h-[140px] flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-border bg-surface-soft/40 p-4 text-center transition hover:border-brand hover:bg-brand/5"
    >
      <span className="text-xs uppercase text-ink-muted">{weekdayOf(day)}, {date}</span>
      <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand/10 text-brand transition group-hover:scale-105 group-hover:bg-brand/15">
        <Icon name="plus" size={18} aria-hidden="true" />
      </span>
      <span className="text-sm font-medium text-ink-muted transition group-hover:text-brand">Запланировать</span>
    </Link>
  );
}

/** Сетка контента: карточки по порядку дней + пустые дни со слотом добавления. */
function FeedGrid({ byDay, onOpen, passes }: { byDay: Map<number, Post[]>; onOpen: (p: Post) => void; passes: (p: Post) => boolean }) {
  const [hidden, setHidden] = useState<string[]>([]);

  type Cell = { key: string } & ({ kind: "post"; post: Post } | { kind: "empty"; day: number });
  const cells: Cell[] = [];
  for (const day of ALL_DAYS) {
    const dayPosts = (byDay.get(day) ?? []).filter((p) => !hidden.includes(p.id));
    if (dayPosts.length === 0) {
      cells.push({ key: `e${day}`, kind: "empty", day });
    } else {
      dayPosts.filter(passes).forEach((p) => cells.push({ key: p.id, kind: "post", post: p }));
    }
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
      {cells.map((c) =>
        c.kind === "post" ? (
          <GridCard key={c.key} post={c.post} onOpen={onOpen} onDelete={(id) => setHidden((h) => [...h, id])} />
        ) : (
          <EmptyDayCard key={c.key} day={c.day} />
        )
      )}
    </div>
  );
}

export default function ContentView() {
  const { surfaceStyle } = useDashboard();
  const [view, setView] = useState<ViewId>("grid");
  const [focusedDay, setFocusedDay] = useState<number | null>(null);
  const [flashDay, setFlashDay] = useState<number | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const router = useRouter();
  const openPost = (p: Post) => router.push(`/dashboard/content/${p.id}`);
  const [chans, setChans] = useState<ChannelId[]>(CHANNEL_ORDER);
  const [types, setTypes] = useState<PostType[]>(POST_TYPE_ORDER);
  const [status, setStatus] = useState<"all" | PostStatus>("all");
  const byDay = postsByDay();

  const toggleChan = (id: ChannelId) =>
    setChans((prev) => (prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]));
  const toggleType = (t: PostType) =>
    setTypes((prev) => (prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]));
  // «Только эта сеть» — иначе приходится выключать остальные по одной
  const onlyChan = (id: ChannelId) =>
    setChans((prev) => (prev.length === 1 && prev[0] === id ? [...CHANNEL_ORDER] : [id]));
  const onlyType = (t: PostType) =>
    setTypes((prev) => (prev.length === 1 && prev[0] === t ? [...POST_TYPE_ORDER] : [t]));
  const passes = (p: Post) =>
    (status === "all" || p.status === status) &&
    types.includes(p.type) &&
    p.channels.some((c) => chans.includes(c));

  const dayRefs = useRef<Map<number, HTMLLIElement>>(new Map());

  // Сфокусироваться на дне: открыть список, подсветить и прокрутить к нему
  const focusDay = (day: number) => {
    setView("list");
    setFocusedDay(day);
    setFlashDay(day);
  };

  // Переход с дашборда: /dashboard/content?day=N → автопрокрутка к дню
  useEffect(() => {
    const raw = new URLSearchParams(window.location.search).get("day");
    const d = raw ? Number(raw) : NaN;
    /* eslint-disable react-hooks/set-state-in-effect */
    if (Number.isInteger(d) && d >= 1 && d <= DAYS_IN_MONTH) focusDay(d);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  // Плавная прокрутка + подсветка при смене сфокусированного дня
  useEffect(() => {
    if (flashDay === null) return;
    const scroll = setTimeout(() => {
      dayRefs.current.get(flashDay)?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 80);
    const clear = setTimeout(() => setFlashDay(null), 1300);
    return () => { clearTimeout(scroll); clearTimeout(clear); };
  }, [flashDay]);

  // Клик вне выделенного поста — снимаем подсветку
  useEffect(() => {
    if (focusedDay === null) return;
    const onDown = (e: MouseEvent) => {
      const li = dayRefs.current.get(focusedDay);
      if (li && li.contains(e.target as Node)) return; // клик внутри поста — оставляем
      setFocusedDay(null);
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [focusedDay]);

  const selectedPosts = selected ? (byDay.get(selected) ?? []).filter(passes) : [];

  return (
    <div className="flex flex-col gap-4">
      {/* Шапка */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-ink sm:text-2xl">Контент-план</h1>
          <p className="mt-0.5 text-sm text-ink-muted">Управляйте постами и публикациями</p>
        </div>
        <Link
          href="/dashboard/create"
          className="btn-glass-blue inline-flex w-full items-center justify-center gap-2 whitespace-nowrap px-4 py-2.5 text-sm font-semibold sm:w-auto"
        >
          <Icon name="sparkles" size={16} aria-hidden="true" />
          Создать контент
        </Link>
      </div>

      <ContentFilters
        view={view}
        onView={setView}
        chans={chans}
        onToggleChan={toggleChan}
        onOnlyChan={onlyChan}
        onAllChans={() => setChans([...CHANNEL_ORDER])}
        types={types}
        onToggleType={toggleType}
        onOnlyType={onlyType}
        onAllTypes={() => setTypes([...POST_TYPE_ORDER])}
        status={status}
        onStatus={setStatus}
      />

      {view === "list" && (
        /* Список: агенда по всем дням месяца */
        <ul className="flex flex-col gap-2">
          {ALL_DAYS.map((day) => {
            const posts = (byDay.get(day) ?? []).filter(passes);
            const dimmed = focusedDay !== null && focusedDay !== day;
            return (
              <li
                key={day}
                ref={(el) => { if (el) dayRefs.current.set(day, el); else dayRefs.current.delete(day); }}
                className={`flex scroll-mt-24 gap-3 rounded-[20px] p-1 transition sm:gap-4 ${
                  focusedDay === day ? "bg-brand/5 ring-1 ring-brand/30" : ""
                } ${flashDay === day ? "uc-flash" : ""} ${dimmed ? "opacity-45" : ""}`}
              >
                <div className="flex w-11 shrink-0 flex-col items-center pt-2">
                  <span className="text-[0.6875rem] uppercase text-ink-muted">{weekdayOf(day)}</span>
                  <span className="font-display text-xl font-bold text-ink">{day}</span>
                </div>
                <div className="min-w-0 flex-1 py-1">
                  {posts.length > 0 ? (
                    <div className="flex flex-col gap-2">
                      {posts.map((p) => <PostCard key={p.id} post={p} onOpen={openPost} />)}
                    </div>
                  ) : (
                    <Link
                      href={`/dashboard/create?day=${day}`}
                      className="group flex items-center justify-between rounded-2xl border border-dashed border-border px-4 py-3 text-sm text-ink-muted transition hover:border-brand hover:bg-brand/5 hover:text-brand"
                    >
                      Свободно
                      <span className="inline-flex items-center gap-1 font-medium text-ink-muted transition group-hover:text-brand">
                        <Icon name="plus" size={14} aria-hidden="true" /> Запланировать
                      </span>
                    </Link>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}

      {view === "grid" && (
        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-success" /> Опубликован</span>
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-brand" /> Запланирован</span>
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-ink-muted" /> Черновик</span>
          </div>
          <FeedGrid byDay={byDay} onOpen={openPost} passes={passes} />
        </div>
      )}

      {view === "calendar" && (
        /* Календарь: числа + цветные точки, тап → панель дня */
        <div className="rounded-[24px] border border-border bg-card p-4 shadow-soft sm:p-6">
          <div className="mb-4 flex items-center gap-2">
            <span className="font-display text-lg font-bold text-ink">{MONTH_LABEL}</span>
          </div>

          <div className="grid grid-cols-7 gap-1.5 sm:gap-2">
            {WEEKDAYS.map((w) => (
              <div key={w} className="pb-1 text-center text-xs font-medium text-ink-muted">{w}</div>
            ))}
            {ALL_DAYS.map((day) => {
              const posts = (byDay.get(day) ?? []).filter(passes);
              const has = posts.length > 0;
              return (
                <button
                  key={day}
                  type="button"
                  onClick={() => has && setSelected(day)}
                  className={`flex h-14 flex-col items-center justify-center gap-1.5 rounded-xl border transition sm:h-16 ${
                    has ? "border-border bg-surface-soft hover:border-brand hover:bg-brand/5" : "border-transparent cursor-default"
                  }`}
                >
                  <span className={`font-display text-sm font-bold sm:text-base ${has ? "text-ink" : "text-ink-muted"}`}>{day}</span>
                  <span className="flex h-1.5 items-center gap-0.5">
                    {posts.slice(0, 3).map((p) => (
                      <span key={p.id} className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[p.status]}`} />
                    ))}
                    {posts.length > 3 && <span className="text-[0.5625rem] font-medium text-ink-muted">+{posts.length - 3}</span>}
                  </span>
                </button>
              );
            })}
          </div>

          <div className="mt-5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-success" /> Опубликован</span>
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-brand" /> Запланирован</span>
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-ink-muted" /> Черновик</span>
          </div>
        </div>
      )}

      {/* Окно дня (из календаря) — по центру */}
      {selected !== null && (
        <div className="fixed inset-0 z-[60] flex items-stretch justify-center sm:items-center sm:p-4">
          <div className="uc-fade-in absolute inset-0 bg-ink/45 backdrop-blur-md" onClick={() => setSelected(null)} aria-hidden="true" />
          <div
            role="dialog"
            aria-modal="true"
            aria-label={`Посты на ${selected} ${MONTH_GEN}`}
            className={`uc-modal-in relative flex h-full w-full flex-col overflow-hidden shadow-lift sm:h-auto sm:max-h-[85vh] sm:max-w-md sm:rounded-3xl ${
              surfaceStyle === "glass"
                ? "border border-white/10 bg-card/90 ring-1 ring-white/5 backdrop-blur-2xl"
                : "border border-border bg-card"
            }`}
          >
            <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-4">
              <div>
                <span className="text-xs uppercase text-ink-muted">{weekdayOf(selected)}</span>
                <h2 className="text-base font-bold text-ink sm:text-lg">{selected} {MONTH_GEN}</h2>
              </div>
              <button type="button" onClick={() => setSelected(null)} aria-label="Закрыть" className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-ink-muted transition hover:bg-surface-soft hover:text-ink">
                <Icon name="close" size={20} aria-hidden="true" />
              </button>
            </div>

            <div className="flex flex-col gap-3 overflow-y-auto px-5 py-5">
              {selectedPosts.map((p) => <PostCard key={p.id} post={p} variant="stack" onOpen={openPost} />)}

              {/* Стеклянная карточка добавления поста в этот день */}
              <Link
                href={`/dashboard/create?day=${selected}`}
                className="btn-glass group flex min-h-[132px] flex-col items-center justify-center gap-2.5 px-4 py-6 text-center"
              >
                <span className="flex h-12 w-12 items-center justify-center rounded-full bg-brand/10 text-brand transition group-hover:scale-105 group-hover:bg-brand/15">
                  <Icon name="plus" size={24} aria-hidden="true" />
                </span>
                <span className="text-sm font-semibold text-ink">Добавить пост</span>
                <span className="text-xs text-ink-muted">на {selected} {MONTH_GEN}</span>
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
