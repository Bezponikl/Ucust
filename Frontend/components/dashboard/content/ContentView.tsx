"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { ChevronLeft, ChevronRight, Gift, Star, Sparkles, X } from "lucide-react";
import { CHANNELS } from "@/lib/channels";
import type { PostStatus } from "@/lib/dashboard/types";
import {
  DAYS_IN_MONTH,
  MONTH_LABEL,
  POSTS,
  STATUS_LABEL,
  WEEKDAYS,
  postsByDay,
  type Post,
  type PostType,
} from "@/lib/dashboard/content";

const STATUS_DOT: Record<PostStatus, string> = {
  published: "bg-success",
  scheduled: "bg-brand",
  draft: "bg-ink-muted",
  none: "bg-transparent",
};

const STATUS_CELL: Record<PostStatus, string> = {
  published: "border-success/40 bg-success/8",
  scheduled: "border-brand/40 bg-brand/8",
  draft: "border-border bg-surface-soft",
  none: "border-border bg-card",
};

const TYPE_ICON: Record<PostType, typeof Gift | null> = {
  promo: Gift,
  review: Star,
  post: null,
};

const TYPE_COLOR: Record<PostType, string> = {
  promo: "text-brand-pink",
  review: "text-brand-orange",
  post: "text-brand",
};

function ChannelIcons({ post }: { post: Post }) {
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
  return <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${cls[status]}`}>{STATUS_LABEL[status]}</span>;
}

export default function ContentView() {
  const [view, setView] = useState<"month" | "list">("month");
  const [selected, setSelected] = useState<number | null>(null);
  const byDay = postsByDay();

  const selectedPosts = selected ? byDay.get(selected) ?? [] : [];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink sm:text-3xl">Контент-план</h1>
          <p className="mt-1 text-sm text-ink-muted">Управляйте постами и публикациями</p>
        </div>
        <div className="flex items-center gap-2">
          <div role="tablist" className="flex gap-1 rounded-xl bg-surface-soft p-1">
            {(["month", "list"] as const).map((v) => (
              <button
                key={v}
                type="button"
                role="tab"
                aria-selected={view === v}
                onClick={() => setView(v)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                  view === v ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
                }`}
              >
                {v === "month" ? "Месяц" : "Список"}
              </button>
            ))}
          </div>
          <Link
            href="/dashboard/create"
            className="btn-glass-blue inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold"
          >
            <Sparkles size={16} aria-hidden="true" />
            <span className="hidden sm:inline">Создать контент</span>
          </Link>
        </div>
      </div>

      {view === "month" ? (
        <div className="rounded-[24px] border border-border bg-card p-4 shadow-soft sm:p-6">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button type="button" aria-label="Предыдущий месяц" className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-muted hover:bg-surface-soft hover:text-ink">
                <ChevronLeft size={18} aria-hidden="true" />
              </button>
              <span className="font-display text-lg font-bold text-ink">{MONTH_LABEL}</span>
              <button type="button" aria-label="Следующий месяц" className="flex h-8 w-8 items-center justify-center rounded-lg text-ink-muted hover:bg-surface-soft hover:text-ink">
                <ChevronRight size={18} aria-hidden="true" />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-7 gap-1.5 sm:gap-2">
            {WEEKDAYS.map((w) => (
              <div key={w} className="pb-1 text-center text-xs font-medium text-ink-muted">{w}</div>
            ))}
            {Array.from({ length: DAYS_IN_MONTH }, (_, i) => i + 1).map((day) => {
              const posts = byDay.get(day) ?? [];
              const top = posts[0];
              const status = top?.status ?? "none";
              const TypeIcon = top ? TYPE_ICON[top.type] : null;
              return (
                <button
                  key={day}
                  type="button"
                  onClick={() => top && setSelected(day)}
                  className={`relative flex aspect-square flex-col rounded-xl border p-1.5 text-left transition sm:p-2 ${STATUS_CELL[status]} ${top ? "hover:ring-1 hover:ring-brand" : "cursor-default"}`}
                >
                  <span className="flex items-start justify-between">
                    {TypeIcon ? <TypeIcon size={13} className={TYPE_COLOR[top!.type]} aria-hidden="true" /> : <span />}
                    {top && <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[status]}`} aria-hidden="true" />}
                  </span>
                  <span className="mt-auto font-display text-sm font-bold text-ink sm:text-base">{day}</span>
                  {top && (
                    <span className="mt-0.5 flex items-center justify-between gap-1">
                      <ChannelIcons post={top} />
                      {posts.length > 1 && <span className="text-[10px] font-medium text-ink-muted">+{posts.length - 1}</span>}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          <div className="mt-5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-success" /> Опубликован</span>
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-brand" /> Запланирован</span>
            <span className="inline-flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-ink-muted" /> Черновик</span>
            <span className="inline-flex items-center gap-1.5"><Gift size={12} className="text-brand-pink" /> Акция</span>
            <span className="inline-flex items-center gap-1.5"><Star size={12} className="text-brand-orange" /> Отзыв</span>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-2.5">
          {[...POSTS].sort((a, b) => a.day - b.day).map((p) => (
            <div key={p.id} className="flex items-center gap-4 rounded-2xl border border-border bg-card p-4 shadow-soft">
              <div className="flex h-12 w-12 shrink-0 flex-col items-center justify-center rounded-xl bg-surface-soft">
                <span className="text-[10px] text-ink-muted">фев</span>
                <span className="font-display text-base font-bold text-ink">{p.day}</span>
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-ink">{p.title}</p>
                <p className="text-xs text-ink-muted">{p.time}</p>
              </div>
              <ChannelIcons post={p} />
              <StatusBadge status={p.status} />
            </div>
          ))}
        </div>
      )}

      {/* Панель дня */}
      {selected !== null && (
        <div className="fixed inset-0 z-[60] flex justify-end">
          <div className="absolute inset-0 bg-ink/40 backdrop-blur-sm" onClick={() => setSelected(null)} aria-hidden="true" />
          <div className="relative ml-auto flex h-full w-full max-w-sm flex-col bg-card p-6 shadow-lift">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-bold text-ink">{selected} февраля</h2>
              <button type="button" onClick={() => setSelected(null)} aria-label="Закрыть" className="flex h-9 w-9 items-center justify-center rounded-full text-ink-muted hover:bg-surface-soft hover:text-ink">
                <X size={20} aria-hidden="true" />
              </button>
            </div>
            <div className="flex flex-col gap-3">
              {selectedPosts.map((p) => (
                <div key={p.id} className="rounded-2xl border border-border bg-surface-soft p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <StatusBadge status={p.status} />
                    <span className="text-xs text-ink-muted">{p.time}</span>
                  </div>
                  <p className="text-sm font-semibold text-ink">{p.title}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <ChannelIcons post={p} />
                    <button type="button" className="text-xs font-medium text-brand hover:text-brand-hover">Открыть</button>
                  </div>
                </div>
              ))}
            </div>
            <Link href="/dashboard/create" className="btn-glass-blue mt-auto inline-flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold">
              <Sparkles size={16} aria-hidden="true" /> Добавить пост
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
