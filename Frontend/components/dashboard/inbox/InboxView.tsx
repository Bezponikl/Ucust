"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
import Checkbox from "@/components/ui/Checkbox";
import ChatPanel from "./ChatPanel";
import { useDashboard, type SurfaceStyle } from "@/components/dashboard/DashboardProvider";
import { menuSurfaceClass, modalSurfaceClass } from "@/lib/dashboard/surface";
import { CHANNELS } from "@/lib/channels";
import {
  INBOX,
  KIND_LABEL,
  type InboxItem,
  type InboxKind,
} from "@/lib/dashboard/inbox";

/* ─── типы ─────────────────────────────────────────────────────── */
type Filter     = "all" | InboxKind | "drafts" | "sent";
type DateFilter = "today" | "7d" | "30d" | "all";

const KIND_FILTERS: { id: Filter; label: string }[] = [
  { id: "all",     label: "Все"           },
  { id: "message", label: "Сообщения"     },
  { id: "comment", label: "Комментарии"   },
  { id: "review",  label: "Отзывы"        },
];

const META_FILTERS: { id: Filter; label: string }[] = [
  { id: "drafts", label: "Черновики"    },
  { id: "sent",   label: "Отправленные" },
];

const DATE_FILTERS: { id: DateFilter; label: string }[] = [
  { id: "today", label: "Сегодня"   },
  { id: "7d",    label: "7 дней"    },
  { id: "30d",   label: "30 дней"   },
  { id: "all",   label: "Всё время" },
];

function passesDates(time: string, df: DateFilter): boolean {
  if (df === "all" || df === "30d") return true;
  const t = time.toLowerCase();
  const isToday = t.includes("мин") || t.includes("ч.");
  if (df === "today") return isToday;
  if (t.includes("вчера")) return true;
  const m = t.match(/(\d+)\s*(дн|дня|день)/);
  if (m) return parseInt(m[1]) <= 6;
  return isToday;
}

/* ─── вспомогательные компоненты ───────────────────────────────── */
function SourceBadge({ item }: { item: InboxItem }) {
  const ch = item.channel ? CHANNELS[item.channel] : null;
  return (
    <span className="inline-flex items-center gap-1 text-xs text-ink-muted">
      {ch?.icon && ch.iconType !== "wordmark" ? (
        <Image src={ch.icon} alt="" width={13} height={13} className="h-[0.8125rem] w-[0.8125rem] object-contain" aria-hidden="true" />
      ) : null}
      {item.sourceLabel}
    </span>
  );
}

function Stars({ rating, size = 12 }: { rating: number; size?: number }) {
  return (
    <span className="inline-flex items-center gap-0.5" aria-label={`${rating} из 5`}>
      {Array.from({ length: 5 }, (_, i) => (
        <Icon key={i} name={i < rating ? "star-bold" : "star"} size={size}
          className={i < rating ? "text-brand-orange" : "text-ink-muted/40"} aria-hidden="true" />
      ))}
    </span>
  );
}

/* ─── модальное окно подтверждения ИИ-автоответа ───────────────── */
function AiConfirmModal({ onConfirm, onCancel, surfaceStyle }: { onConfirm: () => void; onCancel: () => void; surfaceStyle: SurfaceStyle }) {
  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center p-4" onClick={onCancel}>
      <div className={`uc-modal-in isolate relative w-full max-w-md overflow-hidden rounded-3xl shadow-lift ${modalSurfaceClass(surfaceStyle)}`} onClick={(e) => e.stopPropagation()}>
        {/* Шапка */}
        <div className="flex items-center gap-4 border-b border-border px-6 py-5">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand/10">
            <Icon name="sparkles" size={24} className="text-brand" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-base font-bold text-ink sm:text-lg">Включить ИИ-автоответ?</h2>
            <p className="text-sm text-ink-muted">Управление входящими сообщениями</p>
          </div>
          <button type="button" onClick={onCancel} aria-label="Закрыть"
            className="ml-auto flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-ink-muted hover:bg-surface-soft">
            <Icon name="close" size={16} aria-hidden="true" />
          </button>
        </div>

        {/* Тело */}
        <div className="flex flex-col gap-4 px-6 py-5">
          <p className="text-sm leading-relaxed text-ink">
            ИИ будет самостоятельно отвечать на входящие <strong>сообщения и комментарии</strong> в тоне вашего бренда.
            Простые обращения обрабатываются мгновенно без вашего участия.
            Сложные вопросы ИИ оставит в разделе <strong>Черновики</strong> с готовым ответом на проверку.
          </p>

          {/* Предупреждение */}
          <div className="flex items-start gap-3 rounded-2xl border border-brand-orange/30 bg-brand-orange/8 px-4 py-3.5">
            <Icon name="shield" size={18} className="mt-0.5 shrink-0 text-brand-orange" aria-hidden="true" />
            <p className="text-xs leading-relaxed text-ink">
              <span className="block font-semibold text-brand-orange mb-0.5">ИИ может ошибаться</span>
              Как и любые языковые модели, автоответчик может допускать неточности в фактах или тоне.
              Рекомендуем периодически проверять отправленные ответы в разделе <strong>Отправленные</strong>.
            </p>
          </div>

          {/* Что будет делать */}
          <ul className="flex flex-col gap-2 text-sm text-ink">
            {[
              "Отвечает на типовые вопросы о часах, ценах, адресе",
              "Реагирует на отзывы в стиле вашего бренда",
              "Сохраняет черновики для нестандартных обращений",
            ].map((t) => (
              <li key={t} className="flex items-start gap-2">
                <Icon name="check-bold" size={15} className="mt-0.5 shrink-0 text-brand" aria-hidden="true" />
                {t}
              </li>
            ))}
          </ul>
        </div>

        {/* Кнопки */}
        <div className="flex gap-3 border-t border-border px-6 py-4">
          <button type="button" onClick={onCancel}
            className="btn-glass flex-1 inline-flex items-center justify-center px-4 py-3 text-sm font-semibold">
            Отмена
          </button>
          <button type="button" onClick={onConfirm}
            className="btn-glass-blue flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold">
            <Icon name="sparkles" size={15} aria-hidden="true" />
            Включить
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── панель детали (комментарий / отзыв) ───────────────────────── */
interface DetailProps {
  item: InboxItem;
  isAnswered: boolean;
  draftValue: string;
  sentReply?: string;
  onDraftChange: (v: string) => void;
  onSend: () => void;
  onRefresh: () => void;
  onBack: () => void;
}

function DetailPanel({ item, isAnswered, draftValue, sentReply, onDraftChange, onSend, onRefresh, onBack }: DetailProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-[72px] shrink-0 items-center gap-3 border-b border-border/40 px-6">
        <button type="button" onClick={onBack} aria-label="Назад"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-ink-muted transition hover:bg-surface-soft lg:hidden">
          <Icon name="arrow-left" size={18} aria-hidden="true" />
        </button>
        {item.avatar ? (
          <Image src={item.avatar} alt="" width={44} height={44} className="h-11 w-11 shrink-0 rounded-full object-cover" />
        ) : (
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-brand/12 text-sm font-semibold text-brand">
            {item.author.slice(0, 1)}
          </span>
        )}
        <div className="min-w-0 flex-1">
          <div className="text-sm font-semibold text-ink">{item.author}</div>
          <div className="flex items-center gap-2">
            <SourceBadge item={item} />
            <span className="text-[0.6875rem] text-ink-muted">· {item.time}</span>
            {item.rating != null && <Stars rating={item.rating} size={12} />}
          </div>
        </div>
        {isAnswered && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-success/12 px-2.5 py-1 text-xs font-medium text-success">
            <Icon name="check-bold" size={12} aria-hidden="true" /> Отвечено
          </span>
        )}
      </div>

      {/* Переписка прокручивается, форма ответа закреплена внизу — как в мессенджере */}
      <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto px-4 py-4">
        {item.context && (
          <span className="inline-flex w-fit items-center gap-1.5 rounded-full bg-surface-soft px-3 py-1 text-xs text-ink-muted">
            <Icon name="file-text" size={12} aria-hidden="true" /> {item.context}
          </span>
        )}
        <div className="rounded-2xl rounded-tl-md bg-surface-soft px-3.5 py-2.5 text-[0.8125rem] leading-relaxed text-ink">
          {item.text}
        </div>
        {isAnswered && (
          <div className="ml-auto max-w-[85%] rounded-2xl rounded-tr-md bg-brand/10 px-3.5 py-2.5 text-[0.8125rem] leading-relaxed text-ink">
            {sentReply ?? item.sentReply}
          </div>
        )}
      </div>

      {!isAnswered && (
        <div className="shrink-0 border-t border-border/40 px-4 py-3">
          <div className="rounded-2xl border border-brand/20 bg-brand/5 p-3.5">
            <span className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-brand">
              <Icon name="sparkles" size={13} aria-hidden="true" /> ИИ предлагает ответ
            </span>
            <textarea
              value={draftValue}
              onChange={(e) => onDraftChange(e.target.value)}
              className="min-h-20 w-full resize-none rounded-xl border border-border bg-card px-3 py-2 text-[0.8125rem] leading-relaxed text-ink outline-none transition focus:border-brand focus:ring-1 focus:ring-brand/25"
            />
            <div className="mt-2.5 flex flex-wrap gap-2">
              <button type="button" onClick={onSend}
                className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 px-4 py-2 text-sm font-semibold">
                <Icon name="send" size={14} aria-hidden="true" /> Отправить
              </button>
              <button type="button" onClick={onRefresh}
                className="btn-glass inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium">
                <Icon name="refresh" size={14} aria-hidden="true" /> Другой вариант
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── главный компонент ─────────────────────────────────────────── */
export default function InboxView() {
  const [filter,         setFilter]         = useState<Filter>("all");
  const [dateFilter,     setDateFilter]     = useState<DateFilter>("all");
  const [sourceFilter,   setSourceFilter]   = useState<string | null>(null);
  const [unansweredOnly, setUnansweredOnly] = useState(false);
  const [filterMenuOpen, setFilterMenuOpen] = useState(false);
  const filterMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!filterMenuOpen) return;
    const onClick = (e: MouseEvent) => {
      if (filterMenuRef.current && !filterMenuRef.current.contains(e.target as Node)) setFilterMenuOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [filterMenuOpen]);
  const [selectedId,     setSelectedId]     = useState<string | null>("r1");
  const [autoReply,      setAutoReply]      = useState(false);
  const [showAiModal,    setShowAiModal]    = useState(false);
  const [search,         setSearch]         = useState("");
  const tabsRef = useRef<HTMLDivElement>(null);
  const scrollTabs = (dir: "left" | "right") =>
    tabsRef.current?.scrollBy({ left: dir === "right" ? 130 : -130, behavior: "smooth" });
  const [canScrollTabsLeft,  setCanScrollTabsLeft]  = useState(false);
  const [canScrollTabsRight, setCanScrollTabsRight] = useState(false);

  const updateTabsScrollState = () => {
    const el = tabsRef.current;
    if (!el) return;
    setCanScrollTabsLeft(el.scrollLeft > 2);
    setCanScrollTabsRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 2);
  };

  useEffect(() => {
    updateTabsScrollState();
    const el = tabsRef.current;
    el?.addEventListener("scroll", updateTabsScrollState, { passive: true });
    window.addEventListener("resize", updateTabsScrollState);
    return () => {
      el?.removeEventListener("scroll", updateTabsScrollState);
      window.removeEventListener("resize", updateTabsScrollState);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  const [drafts,         setDrafts]         = useState<Record<string, string>>({});
  const [sent,           setSent]           = useState<Record<string, string>>({});
  const [hiddenIds,      setHiddenIds]      = useState<string[]>([]);

  const isAnswered = (i: InboxItem) => i.answered || Boolean(sent[i.id]);
  const draftOf    = (i: InboxItem) => drafts[i.id] ?? i.aiDraft;

  /* Счётчики для табов */
  const counts = useMemo(() => {
    const active = INBOX.filter((i) => !hiddenIds.includes(i.id));
    const unread = (pred: (i: InboxItem) => boolean) => active.filter((i) => !isAnswered(i) && pred(i)).length;
    return {
      all:     unread(() => true),
      message: unread((i) => i.kind === "message"),
      comment: unread((i) => i.kind === "comment"),
      review:  unread((i) => i.kind === "review"),
      drafts:  active.filter((i) => !isAnswered(i)).length,
      sent:    active.filter((i) => isAnswered(i)).length,
    };
  }, [hiddenIds, sent]); // eslint-disable-line react-hooks/exhaustive-deps

  const isMeta = filter === "drafts" || filter === "sent";

  /* Источники, доступные для текущей вкладки по типу (без учёта даты/поиска) */
  const sourceOptions = useMemo(() => {
    const kindPool = INBOX
      .filter((i) => !hiddenIds.includes(i.id))
      .filter((i) => (filter === "all" || isMeta) ? true : i.kind === filter);
    const seen = new Map<string, InboxItem["channel"]>();
    kindPool.forEach((i) => { if (!seen.has(i.sourceLabel)) seen.set(i.sourceLabel, i.channel); });
    return Array.from(seen.entries()).map(([label, channel]) => ({ label, channel }));
  }, [filter, isMeta, hiddenIds]);

  const list = useMemo(() => {
    const q    = search.toLowerCase();
    const base = INBOX
      .filter((i) => !hiddenIds.includes(i.id))
      .filter((i) => !q || i.author.toLowerCase().includes(q) || i.text.toLowerCase().includes(q));
    if (filter === "drafts") return base.filter((i) => !isAnswered(i));
    if (filter === "sent")   return base.filter((i) => isAnswered(i));
    return base
      .filter((i) => filter === "all" ? true : i.kind === filter)
      .filter((i) => sourceFilter ? i.sourceLabel === sourceFilter : true)
      .filter((i) => passesDates(i.time, dateFilter))
      .filter((i) => unansweredOnly ? !isAnswered(i) : true);
  }, [filter, sourceFilter, dateFilter, unansweredOnly, sent, hiddenIds, search]); // eslint-disable-line react-hooks/exhaustive-deps

  const selected = INBOX.find((i) => i.id === selectedId) ?? null;

  const { setMobileChromeHidden, surfaceStyle } = useDashboard();
  // Фон нужен и на мобилке: без него сквозь пустое место просвечивали обои
  const windowSurfaceClass =
    surfaceStyle === "glass"
      ? "bg-card/78 dark:bg-card/55 backdrop-blur-xl"
      : "bg-card";
  useEffect(() => {
    setMobileChromeHidden(Boolean(selected));
    return () => setMobileChromeHidden(false);
  }, [selected, setMobileChromeHidden]);

  const send = (i: InboxItem) => {
    const text = draftOf(i);
    if (!text.trim()) return;
    setSent((s) => ({ ...s, [i.id]: text }));
  };

  const deleteItem = (id: string) => {
    setHiddenIds((h) => [...h, id]);
    if (selectedId === id) setSelectedId(null);
  };

  const handleAiToggle = () => {
    if (autoReply) { setAutoReply(false); return; }
    setShowAiModal(true);
  };

  /* Счётчик таба — показываем только если > 0 */
  const tabCount = (f: Filter): number => counts[f as keyof typeof counts] ?? 0;

  const activeFilterCount =
    (dateFilter !== "all" ? 1 : 0) + (sourceFilter ? 1 : 0) + (unansweredOnly ? 1 : 0);

  const resetFilters = () => {
    setDateFilter("all");
    setSourceFilter(null);
    setUnansweredOnly(false);
  };

  return (
    <>
      {showAiModal && <AiConfirmModal onConfirm={() => { setAutoReply(true); setShowAiModal(false); }} onCancel={() => setShowAiModal(false)} surfaceStyle={surfaceStyle} />}

      <div className={`-mx-6 -mt-5 -mb-24 flex overflow-hidden sm:-mx-8 lg:mx-0 lg:mb-0 lg:mt-0 lg:h-[calc(100dvh-56px-44px)] lg:rounded-3xl lg:border lg:border-border lg:shadow-soft ${windowSurfaceClass} ${selected ? "h-dvh" : "h-[calc(100dvh-56px-6rem)]"}`}>

        {/* ── ЛЕВАЯ ПАНЕЛЬ ───────────────────────────────────────── */}
        {/* На мобилке список занимает всю ширину: фикс w-80 оставлял полосу справа */}
        <div className={`flex w-full shrink-0 flex-col border-r border-border/40 lg:w-80 xl:w-96 ${selected ? "hidden lg:flex" : "flex"}`}>

          {/* Заголовок */}
          <div className="flex h-[72px] shrink-0 items-center border-b border-border/40 px-5">
            <h1 className="text-xl font-bold text-ink sm:text-2xl">Входящие</h1>
          </div>

          {/* ИИ-автоответ */}
          <div className="shrink-0 border-b border-border/40 px-3 py-3">
            <button
              type="button"
              onClick={handleAiToggle}
              aria-pressed={autoReply}
              className={`flex w-full items-center gap-3 rounded-2xl border px-3.5 py-3 text-left shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift ${
                autoReply
                  ? "border-brand/30 bg-brand/8 hover:bg-brand/12"
                  : "border-border bg-surface-soft hover:border-brand/30"
              }`}
            >
              <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl transition ${autoReply ? "bg-brand" : "bg-card"}`}>
                <Icon name="sparkles" size={18} className={autoReply ? "text-white" : "text-ink-muted"} aria-hidden="true" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-ink">ИИ-автоответ</p>
                <p className="text-xs text-ink-muted">
                  {autoReply ? "Активен — ИИ отвечает автоматически" : "Нажмите, чтобы включить"}
                </p>
              </div>
              <div className={`relative h-5 w-9 shrink-0 rounded-full transition-colors ${autoReply ? "bg-brand" : "bg-ink-muted/30"}`}>
                <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${autoReply ? "translate-x-4" : "translate-x-0.5"}`} />
              </div>
            </button>
          </div>

          {/* Поиск */}
          <div className="shrink-0 border-b border-border/40 px-3 py-2">
            <div className="flex items-center gap-2 rounded-xl bg-surface-soft px-3 py-2">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
                strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 shrink-0 text-ink-muted" aria-hidden="true">
                <circle cx="11" cy="11" r="7" /><path d="m21 21-4.35-4.35" />
              </svg>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Поиск"
                className="min-w-0 flex-1 bg-transparent text-sm text-ink outline-none placeholder:text-ink-muted"
              />
              {search && (
                <button type="button" onClick={() => setSearch("")} aria-label="Очистить">
                  <Icon name="close" size={13} className="text-ink-muted hover:text-ink" aria-hidden="true" />
                </button>
              )}
            </div>
          </div>

          {/* Горизонтальные таблетки-фильтры — следующая вкладка естественно обрезается краем (как в Telegram); стрелки прозрачные, лежат поверх текста и проявляются при наведении на зону */}
          <div className="group/tabs relative shrink-0 border-b border-border/40">
            <div ref={tabsRef} className="flex gap-1 overflow-x-auto px-1 py-1.5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
              {[...KIND_FILTERS, ...META_FILTERS].map((f) => {
                const n  = tabCount(f.id);
                const on = filter === f.id;
                return (
                  <button key={f.id} type="button" onClick={() => { setFilter(f.id); setSelectedId(null); setSourceFilter(null); setFilterMenuOpen(false); }}
                    className={`flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full px-3 py-1.5 text-[0.8125rem] font-medium transition-colors ${
                      on ? "bg-brand/10 text-brand" : "text-ink-muted hover:bg-surface-soft hover:text-ink"
                    }`}>
                    {f.label}
                    {n > 0 && (
                      <span className={`rounded-full px-1.5 py-px text-[0.625rem] font-bold ${on ? "bg-brand/20 text-brand" : "bg-surface-soft text-ink-muted"}`}>{n}</span>
                    )}
                  </button>
                );
              })}
            </div>
            {canScrollTabsLeft && (
              <button type="button" onClick={() => scrollTabs("left")} aria-label="Прокрутить влево"
                className="absolute left-1 top-1/2 flex h-7 w-7 -translate-x-1 -translate-y-1/2 items-center justify-center rounded-full bg-card/90 text-ink-muted opacity-0 shadow-sm backdrop-blur-sm transition-all duration-200 hover:bg-surface-soft hover:text-ink group-hover/tabs:translate-x-0 group-hover/tabs:opacity-100">
                <Icon name="chevron-left" size={14} aria-hidden="true" />
              </button>
            )}
            {canScrollTabsRight && (
              <button type="button" onClick={() => scrollTabs("right")} aria-label="Прокрутить вправо"
                className="absolute right-1 top-1/2 flex h-7 w-7 translate-x-1 -translate-y-1/2 items-center justify-center rounded-full bg-card/90 text-ink-muted opacity-0 shadow-sm backdrop-blur-sm transition-all duration-200 hover:bg-surface-soft hover:text-ink group-hover/tabs:translate-x-0 group-hover/tabs:opacity-100">
                <Icon name="chevron-right" size={14} aria-hidden="true" />
              </button>
            )}
          </div>

          {/* Фильтр (период + источник + без ответа) — единая кнопка, скрыта на мета-вкладках */}
          {!isMeta && (
            <div ref={filterMenuRef} className="relative shrink-0 border-t border-border/40 px-3 py-2.5">
              <button type="button" onClick={() => setFilterMenuOpen((v) => !v)} aria-expanded={filterMenuOpen}
                className="flex w-full items-center gap-2 rounded-xl border border-border bg-surface-soft px-3 py-2 text-left transition hover:border-brand/30">
                <Icon name="sliders" size={14} className="shrink-0 text-ink-muted" aria-hidden="true" />
                <span className="text-xs font-medium text-ink">Фильтр</span>
                {activeFilterCount > 0 && (
                  <span className="rounded-full bg-brand px-1.5 py-px text-[0.625rem] font-bold text-white">{activeFilterCount}</span>
                )}
                <Icon name="chevron-down" size={14} className={`ml-auto shrink-0 text-ink-muted transition-transform ${filterMenuOpen ? "rotate-180" : ""}`} aria-hidden="true" />
              </button>

              {filterMenuOpen && (
                <div className={`absolute left-3 right-3 top-full z-30 mt-1.5 max-h-[70vh] overflow-y-auto rounded-2xl border border-border p-4 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}>
                  <p className="text-[0.6875rem] font-semibold uppercase tracking-wide text-ink-muted">Период</p>
                  <div className="mt-1.5 flex flex-wrap gap-1">
                    {DATE_FILTERS.map((d) => {
                      const on = dateFilter === d.id;
                      return (
                        <button key={d.id} type="button" onClick={() => setDateFilter(d.id)}
                          className={`rounded-full px-2.5 py-1 text-xs font-medium transition ${on ? "bg-brand text-white" : "bg-surface-soft text-ink-muted hover:text-ink"}`}>
                          {d.label}
                        </button>
                      );
                    })}
                  </div>

                  {sourceOptions.length > 1 && (
                    <>
                      <p className="mt-4 text-[0.6875rem] font-semibold uppercase tracking-wide text-ink-muted">Источник</p>
                      <div className="mt-1.5 flex flex-wrap gap-1">
                        <button type="button" onClick={() => setSourceFilter(null)}
                          className={`rounded-full px-2.5 py-1 text-xs font-medium transition ${!sourceFilter ? "bg-brand text-white" : "bg-surface-soft text-ink-muted hover:text-ink"}`}>
                          Все
                        </button>
                        {sourceOptions.map(({ label, channel }) => {
                          const on = sourceFilter === label;
                          const meta = channel ? CHANNELS[channel] : null;
                          return (
                            <button key={label} type="button" onClick={() => setSourceFilter(label)}
                              className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium transition ${on ? "bg-brand text-white" : "bg-surface-soft text-ink-muted hover:text-ink"}`}>
                              {meta?.icon && meta.iconType !== "wordmark" && (
                                <Image src={meta.icon} alt="" width={13} height={13} className="h-[0.8125rem] w-[0.8125rem] object-contain" aria-hidden="true" />
                              )}
                              {label}
                            </button>
                          );
                        })}
                      </div>
                    </>
                  )}

                  <div className="mt-4 border-t border-border/40 pt-3">
                    <label className="flex cursor-pointer items-center gap-2 text-xs text-ink-muted">
                      <Checkbox checked={unansweredOnly} onChange={(e) => setUnansweredOnly(e.target.checked)} />
                      Только без ответа
                    </label>
                  </div>

                  {activeFilterCount > 0 && (
                    <button type="button" onClick={resetFilters}
                      className="mt-4 w-full rounded-xl border border-border px-3 py-2 text-center text-xs font-medium text-ink-muted transition hover:bg-surface-soft hover:text-ink">
                      Сбросить фильтры
                    </button>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Список */}
          <ul className="flex flex-1 flex-col gap-1.5 overflow-y-auto px-2 py-2">
            {list.length === 0 && (
              <li className="rounded-2xl border border-dashed border-border px-4 py-8 text-center text-sm text-ink-muted">
                {filter === "sent" ? "Нет отправленных ответов" : filter === "drafts" ? "Черновиков нет" : "Нет обращений по фильтру"}
              </li>
            )}
            {list.map((i) => {
              const answered = isAnswered(i);
              const on       = selectedId === i.id;
              return (
                <li key={i.id} className="group relative">
                  <button type="button" onClick={() => setSelectedId(i.id)}
                    className={`w-full rounded-xl border px-3 py-2.5 text-left transition ${on ? "border-brand/40 bg-brand/6" : "border-border/30 bg-card hover:bg-surface-soft"}`}>
                    <div className="flex items-start gap-2.5">
                      {i.avatar ? (
                        <Image src={i.avatar} alt="" width={36} height={36} className="h-9 w-9 shrink-0 rounded-full object-cover" />
                      ) : (
                        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand/12 text-sm font-semibold text-brand">
                          {i.author.slice(0, 1)}
                        </span>
                      )}
                      <div className="min-w-0 flex-1 pr-5">
                        <div className="flex items-center justify-between gap-1">
                          <span className="flex min-w-0 items-center gap-1.5">
                            <span className="truncate text-[0.8125rem] font-semibold text-ink">{i.author}</span>
                            {!answered && <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-brand" aria-label="Без ответа" />}
                          </span>
                          <span className="shrink-0 text-[0.625rem] text-ink-muted">{i.time}</span>
                        </div>
                        <div className="mt-0.5 flex flex-col gap-0.5">
                          <div className="flex h-3.5 items-center">
                            {i.rating != null && <Stars rating={i.rating} size={11} />}
                          </div>
                          <p className="line-clamp-1 text-[0.6875rem] leading-snug text-ink-muted">{i.text}</p>
                        </div>
                      </div>
                    </div>
                  </button>

                  {/* Удалить — hover */}
                  <button type="button" onClick={(e) => { e.stopPropagation(); deleteItem(i.id); }}
                    aria-label={`Удалить обращение от ${i.author}`}
                    className="absolute right-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded-full text-ink-muted opacity-0 transition hover:bg-red-500/10 hover:text-red-500 group-hover:opacity-100">
                    <Icon name="trash" size={12} aria-hidden="true" />
                  </button>
                </li>
              );
            })}
          </ul>
        </div>

        {/* ── ПРАВАЯ ПАНЕЛЬ ──────────────────────────────────────── */}
        <div className={`flex min-w-0 flex-1 flex-col ${selected ? "flex" : "hidden lg:flex"}`}>
          {!selected ? (
            <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand/10">
                <Icon name="message" size={26} className="text-brand/60" aria-hidden="true" />
              </div>
              <p className="text-sm font-medium text-ink-muted">Выберите обращение слева</p>
            </div>
          ) : selected.kind === "message" ? (
            <ChatPanel key={selected.id} item={selected} onBack={() => setSelectedId(null)} />
          ) : (
            <DetailPanel
              key={selected.id}
              item={selected}
              isAnswered={isAnswered(selected)}
              draftValue={draftOf(selected)}
              sentReply={sent[selected.id]}
              onDraftChange={(v) => setDrafts((d) => ({ ...d, [selected.id]: v }))}
              onSend={() => send(selected)}
              onRefresh={() => setDrafts((d) => ({ ...d, [selected.id]: selected.aiDraft }))}
              onBack={() => setSelectedId(null)}
            />
          )}
        </div>
      </div>
    </>
  );
}
