"use client";

import { useState } from "react";
import { Star, Sparkles, Send } from "lucide-react";
import {
  PLATFORM_LABEL,
  REVIEWS,
  reviewStats,
  type Review,
} from "@/lib/dashboard/reviews";

type Filter = "all" | "new" | "unanswered";

function Stars({ rating }: { rating: number }) {
  return (
    <span className="flex items-center gap-0.5" aria-label={`Оценка ${rating} из 5`}>
      {Array.from({ length: 5 }, (_, i) => (
        <Star
          key={i}
          size={14}
          className={i < rating ? "fill-brand-orange text-brand-orange" : "text-border"}
          aria-hidden="true"
        />
      ))}
    </span>
  );
}

function ReviewCard({ review }: { review: Review }) {
  const [replying, setReplying] = useState(false);
  const [draft, setDraft] = useState(review.aiDraft);
  const [sent, setSent] = useState<string | null>(review.reply);

  return (
    <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-tint text-sm font-semibold text-brand">
            {review.author.slice(0, 1)}
          </span>
          <div>
            <p className="text-sm font-semibold text-ink">{review.author}</p>
            <div className="mt-0.5 flex items-center gap-2">
              <Stars rating={review.rating} />
              <span className="rounded-full bg-surface-soft px-2 py-0.5 text-[11px] font-medium text-ink-muted">
                {PLATFORM_LABEL[review.platform]}
              </span>
            </div>
          </div>
        </div>
        <span className="shrink-0 text-xs text-ink-muted">{review.date}</span>
      </div>

      <p className="mt-3 text-sm leading-relaxed text-ink">{review.text}</p>

      {sent ? (
        <div className="mt-4 rounded-2xl border-l-2 border-l-brand bg-surface-soft p-4">
          <p className="mb-1 text-xs font-semibold text-brand">Ваш ответ</p>
          <p className="text-sm text-ink">{sent}</p>
        </div>
      ) : replying ? (
        <div className="mt-4">
          <div className="mb-2 inline-flex items-center gap-1.5 rounded-full bg-brand-tint px-2.5 py-1 text-[11px] font-medium text-brand">
            <Sparkles size={12} aria-hidden="true" /> Черновик от AI
          </div>
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            className="min-h-24 w-full resize-none rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition focus:border-brand focus:ring-2 focus:ring-brand-tint"
          />
          <div className="mt-2 flex gap-2">
            <button
              type="button"
              onClick={() => setSent(draft)}
              className="btn-glass-blue inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold"
            >
              <Send size={14} aria-hidden="true" /> Отправить
            </button>
            <button
              type="button"
              onClick={() => setReplying(false)}
              className="btn-glass inline-flex items-center rounded-xl px-4 py-2.5 text-sm font-semibold"
            >
              Отмена
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setReplying(true)}
          className="btn-glass mt-4 inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold"
        >
          <Sparkles size={14} aria-hidden="true" /> Ответить с AI
        </button>
      )}
    </div>
  );
}

export default function ReviewsView() {
  const [filter, setFilter] = useState<Filter>("all");
  const stats = reviewStats();

  const filtered = REVIEWS.filter((r) => {
    if (filter === "unanswered") return !r.reply;
    if (filter === "new") return r.date === "сегодня" || r.date === "вчера";
    return true;
  });

  const FILTERS: { id: Filter; label: string }[] = [
    { id: "all", label: "Все" },
    { id: "new", label: "Новые" },
    { id: "unanswered", label: "Без ответа" },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink sm:text-3xl">Отзывы</h1>
          <p className="mt-1 text-sm text-ink-muted">Отвечайте быстро — AI поможет с текстом</p>
        </div>
        <div className="flex items-center gap-4 rounded-2xl border border-border bg-card px-5 py-3 shadow-soft">
          <div className="text-center">
            <p className="flex items-center gap-1 font-display text-2xl font-extrabold text-ink">
              {stats.avg} <Star size={16} className="fill-brand-orange text-brand-orange" aria-hidden="true" />
            </p>
            <p className="text-xs text-ink-muted">Средний рейтинг</p>
          </div>
          <div className="h-9 w-px bg-border" />
          <div className="text-center">
            <p className="font-display text-2xl font-extrabold text-ink">{stats.unanswered}</p>
            <p className="text-xs text-ink-muted">Без ответа</p>
          </div>
        </div>
      </div>

      <div role="tablist" className="flex gap-1 self-start rounded-xl bg-surface-soft p-1">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            type="button"
            role="tab"
            aria-selected={filter === f.id}
            onClick={() => setFilter(f.id)}
            className={`rounded-lg px-4 py-1.5 text-sm font-medium transition ${
              filter === f.id ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="flex flex-col gap-4">
        {filtered.map((r) => (
          <ReviewCard key={r.id} review={r} />
        ))}
        {filtered.length === 0 && (
          <p className="rounded-2xl border border-border bg-card p-8 text-center text-sm text-ink-muted">
            Нет отзывов в этом фильтре.
          </p>
        )}
      </div>
    </div>
  );
}
