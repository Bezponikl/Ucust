"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import { toast } from "@/lib/toast";
import { useDashboard } from "@/components/dashboard/DashboardProvider";
import CreateProjectNotice from "@/components/dashboard/CreateProjectNotice";
import { analyzeChannel, getChannelSettings, updateChannelSettings } from "@/lib/api/orchestration";
import { getProject } from "@/lib/api/projects";
import { toMessage } from "@/lib/api/errors";
import { channelMetrics } from "@/lib/api/mapGeneration";
import type { ChannelAnalysisResponse, ChannelPostDto, ChannelSettingsResponse } from "@/lib/api/types";

const LIMITS = [10, 20, 30, 50];

/** Интервалы автоскана в часах — настраиваются пользователем. */
const INTERVAL_HOURS = [1, 3, 6, 12, 24, 48];

/** @keep — как на бэке (normalizeChannel): ссылка/хэндл → @handle. */
function normalizeChannel(raw: string): string {
  let s = raw.trim();
  if (s.includes("t.me/")) s = s.substring(s.indexOf("t.me/") + "t.me/".length);
  if (s.includes("/")) s = s.substring(s.lastIndexOf("/") + 1);
  if (!s.startsWith("@")) s = `@${s.replace(/^@+/, "")}`;
  return s;
}

function fmtDate(iso?: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("ru-RU", { day: "numeric", month: "short" });
}

function fmtDateTime(iso?: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("ru-RU", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

function mediaLabel(post: ChannelPostDto): string | null {
  const t = (post.mediaType ?? "").toLowerCase();
  if (!t) return null;
  if (t.includes("photo") || t.includes("image") || t.includes("video")) return "с медиа";
  if (t.includes("text")) return "текст";
  return t;
}

/** Метрика поста канала: значение + иконка. 0/null не показываем. */
function Metric({ icon, value, label }: { icon: "eye" | "arrow-right" | "message"; value?: number | null; label: string }) {
  if (!value || value <= 0) return null;
  return (
    <span className="inline-flex items-center gap-1 text-ink-muted" title={label}>
      <Icon name={icon} size={13} aria-hidden="true" />
      {channelMetrics(value)}
    </span>
  );
}

function summaryNumber(info: Record<string, unknown> | null, key: string): number | null {
  const v = info?.[key];
  return typeof v === "number" ? v : typeof v === "string" && !Number.isNaN(Number(v)) ? Number(v) : null;
}

export default function ChannelAnalysisView() {
  const router = useRouter();
  const { projectId, hasProject, data } = useDashboard();

  const [channel, setChannel] = useState("");
  const [limit, setLimit] = useState(10);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<ChannelAnalysisResponse | null>(null);
  const [boundChannel, setBoundChannel] = useState<string | null>(null);
  const [settings, setSettings] = useState<ChannelSettingsResponse | null>(null);
  const [settingsBusy, setSettingsBusy] = useState(false);
  const reqId = useRef(0);

  // Привязанный к проекту Telegram-канал (socialLinks.telegram). Аналитика
  // доступна только для привязанной соцсети: поле ввода блокируется, сам анализ
  // без привязки не запускается (бэк отвечает 400 CHANNEL_NOT_BOUND).
  useEffect(() => {
    if (!projectId) return;
    let cancelled = false;
    void getProject(projectId)
      .then((p) => {
        if (cancelled) return;
        const telegram = p.socialLinks?.telegram;
        if (!telegram || !telegram.trim()) {
          setBoundChannel(null);
          setChannel("");
          return;
        }
        const bound = normalizeChannel(telegram);
        setBoundChannel(bound);
        setChannel(bound);
      })
      .catch(() => {
        // Проект без соцсетей — остаётся пустое поле, анализ заблокирован.
      });
    return () => { cancelled = true; };
  }, [projectId]);

  // Настройки автоскана канала проекта (интервал часов, время последнего скана).
  useEffect(() => {
    if (!projectId || !boundChannel) return;
    let cancelled = false;
    void getChannelSettings(projectId)
      .then((s) => {
        if (cancelled) return;
        setSettings(s);
      })
      .catch(() => {
        // Интервал остаётся по умолчанию (6 ч) — блок авто-пересканирования скрыт.
      });
    return () => { cancelled = true; };
  }, [projectId, boundChannel]);

  const changeInterval = async (hours: number) => {
    if (!projectId) return;
    setSettingsBusy(true);
    try {
      const s = await updateChannelSettings(projectId, hours);
      setSettings(s);
    } catch (err) {
      setError(toMessage(err));
      toast("Не удалось сохранить интервал автоскана");
    } finally {
      setSettingsBusy(false);
    }
  };

  const run = async () => {
    if (!projectId) return;
    const trimmed = channel.trim();
    if (!trimmed) {
      toast("Укажите канал — @handle или ссылку t.me/...");
      return;
    }
    setBusy(true);
    setError(null);
    const id = ++reqId.current;
    try {
      const res = await analyzeChannel({ projectId, channel: trimmed, limit });
      if (id !== reqId.current) return;
      setAnalysis(res);
      if (res.status === "FAILED") setError(res.error ?? "Не удалось проанализировать канал");
    } catch (err) {
      if (id === reqId.current) {
        setError(toMessage(err));
        toast("Анализ канала не запустился — проверьте, что контур доступен");
      }
    } finally {
      if (id === reqId.current) setBusy(false);
    }
  };

  /** Пост-ответ на возражение: сеем промпт и уводим в создание публикации. */
  const respondToObjection = (objection: string) => {
    try {
      sessionStorage.setItem(
        "uc_ai_prompt",
        `Напиши пост-ответ на возражение аудитории из комментариев: «${objection}». Сними сомнение, покажи пользу и позови к действию.`,
      );
    } catch {}
    router.push("/dashboard/create");
  };

  const posts = analysis?.posts ?? [];
  const objections = analysis?.objections ?? [];
  const subscribers = summaryNumber(analysis?.channelInfo ?? null, "subscribers");
  const avgViews = summaryNumber(analysis?.channelInfo ?? null, "avgViewsPerPost");
  const done = analysis?.status === "COMPLETED";

  if (!hasProject || !data?.businessName?.trim()) {
    return (
      <div className="flex flex-col gap-6 sm:gap-8">
        <div>
          <h1 className="text-xl font-bold text-ink sm:text-2xl">Анализ канала</h1>
          <p className="mt-0.5 text-sm text-ink-muted">Что публикует Telegram-канал и как аудитория отвечает</p>
        </div>
        <CreateProjectNotice />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Шапка */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-ink sm:text-2xl">Анализ канала</h1>
          <p className="mt-0.5 text-sm text-ink-muted">Импортированные посты появляются в контент-плане с метриками</p>
        </div>
      </div>

      {/* Форма запуска */}
      {!boundChannel ? (
        <div className="rounded-2xl border border-border bg-card p-4 shadow-soft sm:p-5">
          <div className="flex items-start gap-3">
            <Icon name="send" size={18} className="mt-0.5 shrink-0 text-brand" aria-hidden="true" />
            <div>
              <p className="text-sm font-bold text-ink">Анализ станет доступен после привязки Telegram</p>
              <p className="mt-1 text-sm text-ink-muted">
                Сначала привяжите Telegram-канал проекта в разделе «Бизнес» (этап подключения соцсетей:
                PATCH /projects socialLinks.telegram). После этого здесь появится анализ постов с метриками
                и авто-пересканирование раз в настроенный интервал.
              </p>
            </div>
          </div>
        </div>
      ) : (
      <div className="rounded-2xl border border-border bg-card p-4 shadow-soft sm:p-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="min-w-0 flex-1">
            <span className="mb-1.5 block text-sm font-medium text-ink-muted">Телеграм-канал (привязанный)</span>
            <input
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") void run(); }}
              placeholder="@nazvanie_kanala или https://t.me/nazvanie_kanala"
              readOnly
              disabled={!boundChannel}
              className="w-full cursor-not-allowed rounded-2xl border border-border bg-surface-soft px-4 py-2.5 text-sm text-ink outline-none transition placeholder:text-ink-muted/60 focus:border-brand/50"
            />
            <p className="mt-1 text-xs text-ink-muted">Анализируется только канал, привязанный к проекту.</p>
          </div>
          <div>
            <span className="mb-1.5 block text-sm font-medium text-ink-muted">Постов</span>
            <div className="flex items-center gap-1 rounded-2xl border border-border bg-surface-soft p-1">
              {LIMITS.map((n) => (
                <button
                  key={n}
                  type="button"
                  onClick={() => setLimit(n)}
                  aria-pressed={limit === n}
                  className={`rounded-xl px-2.5 py-1.5 text-sm font-medium transition ${limit === n ? "bg-card text-brand shadow-soft" : "text-ink-muted hover:text-ink"}`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>
          <button
            type="button"
            onClick={() => void run()}
            disabled={busy}
            className="btn-glass-blue inline-flex items-center justify-center gap-2 rounded-full px-5 py-2.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Icon name={busy ? "refresh" : "chart-line"} size={16} className={busy ? "animate-spin" : ""} aria-hidden="true" />
            {busy ? "Анализируем…" : analysis ? "Пересканировать" : "Анализировать"}
          </button>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 border-t border-border pt-2.5 text-xs text-ink-muted">
          <label className="inline-flex items-center gap-2">
            <span>Авто-пересканирование</span>
            <select
              value={settings?.autoRescanIntervalHours ?? 6}
              onChange={(e) => void changeInterval(Number(e.target.value))}
              disabled={settingsBusy}
              aria-label="Интервал авто-пересканирования"
              className="rounded-lg border border-border bg-surface-soft px-2 py-1 text-xs font-medium text-ink outline-none transition focus:border-brand/50 disabled:opacity-60"
            >
              {INTERVAL_HOURS.map((h) => (
                <option key={h} value={h}>каждые {h} ч</option>
              ))}
            </select>
          </label>
          <span>последний скан: {fmtDateTime(settings?.lastRescanAt)}</span>
          {settingsBusy && <Icon name="refresh" size={13} className="animate-spin text-brand" aria-hidden="true" />}
        </div>
        <p className="mt-2.5 text-xs text-ink-muted">
          Бот читает публикации канала, собирает просмотры и возражения в комментариях, а посты кладёт в контент-план как опубликованные.
        </p>
      </div>
      )}

      {error && (
        <div className="flex items-start gap-2 rounded-2xl border border-red-400/30 bg-red-500/8 px-4 py-3 text-sm text-[#e5484d]">
          <Icon name="close" size={16} className="mt-0.5 shrink-0" aria-hidden="true" />
          <span>{error}</span>
        </div>
      )}

      {analysis && done && (
        <div className="flex flex-col gap-4">
          {/* Сводка по каналу */}
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-border bg-surface-soft/60 p-4">
              <span className="text-xs text-ink-muted">Канал</span>
              <p className="mt-0.5 truncate text-base font-bold text-ink">{analysis.channel}</p>
              <p className="mt-0.5 text-xs text-ink-muted">постов разобрано: {posts.length === 0 ? "—" : posts.length}</p>
            </div>
            <div className="rounded-2xl border border-border bg-surface-soft/60 p-4">
              <span className="text-xs text-ink-muted">Подписчиков</span>
              <p className="mt-0.5 text-base font-bold text-ink">{subscribers === null ? "—" : channelMetrics(subscribers)}</p>
              <p className="mt-0.5 text-xs text-ink-muted">охват аудитории канала</p>
            </div>
            <div className="rounded-2xl border border-border bg-surface-soft/60 p-4">
              <span className="text-xs text-ink-muted">Просмотров в среднем</span>
              <p className="mt-0.5 text-base font-bold text-ink">{avgViews === null ? "—" : channelMetrics(avgViews)}</p>
              <p className="mt-0.5 text-xs text-ink-muted">на пост за последние публикации</p>
            </div>
          </div>

          {/* Возражения аудитории */}
          <div className="rounded-2xl border border-border bg-card p-4 shadow-soft sm:p-5">
            <div className="mb-3 flex items-center justify-between gap-2">
              <span className="text-sm font-bold text-ink">Возражения аудитории</span>
              {objections.length > 0 && (
                <button
                  type="button"
                  onClick={() => respondToObjection(objections[0])}
                  className="inline-flex items-center gap-1.5 rounded-full border border-brand/30 bg-brand/5 px-3 py-1.5 text-xs font-semibold text-brand transition hover:bg-brand/10"
                >
                  <Icon name="sparkles" size={13} aria-hidden="true" /> Пост-ответ на главное возражение
                </button>
              )}
            </div>
            {objections.length === 0 ? (
              <p className="text-sm text-ink-muted">Контур не нашёл возражений в комментариях — либо канал их не комментируют, либо в выборку не попали.</p>
            ) : (
              <ul className="flex flex-col gap-2">
                {objections.map((obj, i) => (
                  <li key={i} className="flex items-center justify-between gap-3 rounded-xl border border-border bg-surface-soft/50 px-3.5 py-2.5">
                    <span className="min-w-0 flex-1 text-sm text-ink">{obj}</span>
                    <button
                      type="button"
                      onClick={() => respondToObjection(obj)}
                      className="shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold text-brand transition hover:bg-brand/10"
                    >
                      Ответить
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Посты канала */}
          <div className="rounded-2xl border border-border bg-card p-4 shadow-soft sm:p-5">
            <span className="mb-3 block text-sm font-bold text-ink">Что публикует канал</span>
            {posts.length === 0 ? (
              <p className="text-sm text-ink-muted">Постов в ответе контура не оказалось — можно запустить пересканирование с бо́льшим лимитом.</p>
            ) : (
              <ul className="flex flex-col gap-2.5">
                {posts.map((p) => (
                  <li key={p.externalId} className="flex flex-col gap-1.5 rounded-xl border border-border bg-surface-soft/50 px-3.5 py-3">
                    <div className="flex items-center gap-2 text-xs text-ink-muted">
                      <Icon name="send" size={12} aria-hidden="true" />
                      <span>{fmtDate(p.date)}</span>
                      {mediaLabel(p) && <span className="rounded-full bg-card px-2 py-0.5 text-[0.6875rem] font-medium text-ink-muted">{mediaLabel(p)}</span>}
                    </div>
                    <p className="line-clamp-3 text-sm leading-relaxed text-ink">{p.text}</p>
                    <div className="flex flex-wrap items-center gap-3">
                      <Metric icon="eye" value={p.views} label="Просмотры" />
                      <Metric icon="arrow-right" value={p.forwards} label="Репосты" />
                      <Metric icon="message" value={p.commentsCount} label="Комментарии" />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {analysis && analysis.status === "PENDING" && (
        <div className="flex items-center gap-2 rounded-2xl border border-border bg-surface-soft/60 px-4 py-3 text-sm text-ink-muted">
          <Icon name="refresh" size={15} className="animate-spin text-brand" aria-hidden="true" />
          Анализ выполняется — результат придёт в контент-план автоматически.
        </div>
      )}

      {!analysis && !busy && (
        <p className="inline-flex items-start gap-1.5 text-sm text-ink-muted">
          <Icon name="arrow-left" size={14} className="mt-0.5 shrink-0" aria-hidden="true" />
          Запустите анализ — возражения из комментариев станут основой для постов-ответов.
        </p>
      )}
    </div>
  );
}