"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";
import { toast } from "@/lib/toast";
import ModalShell from "@/components/ModalShell";
import PromoPreview from "@/components/dashboard/promos/PromoPreview";
import { fmtPeriod } from "@/lib/dashboard/date";
import {
  PROMO_STATUS_LABEL,
  fmtNum,
  promoProgress,
  type Promo,
  type PromoStatus,
} from "@/lib/dashboard/promos";
import AiSidebar from "./edit/AiSidebar";
import { draftFromPromo, type PromoDraft } from "./edit/draft";
import { ContentTab, InfoTab, MechanicsTab, PublishTab, StatsTab, type AiKey } from "./edit/tabs";
import { Card } from "./edit/fields";

type TabId = "info" | "mechanics" | "content" | "publish" | "stats";

const TABS: { id: TabId; label: string; icon: IconName }[] = [
  { id: "info", label: "Информация", icon: "file-text" },
  { id: "mechanics", label: "Механика", icon: "sliders" },
  { id: "content", label: "Контент", icon: "image" },
  { id: "publish", label: "Публикация", icon: "send" },
  { id: "stats", label: "Статистика", icon: "bar-chart" },
];

const STATUS_DOT: Record<PromoStatus, string> = {
  active: "bg-success",
  scheduled: "bg-brand",
  finished: "bg-ink-muted",
};

/* ── Мок-варианты ИИ: в проде здесь ответ модели ── */
const VARIANTS = {
  title: [
    "Счастливые часы",
    "Горячее предложение для гостей",
    "Время экономить на любимом кофе",
    "Только по будням: выгода на всё меню",
  ],
  description: [
    "Порадуйте себя в перерыве: скидка на все напитки каждый будний день с 15:00 до 17:00.",
    "Успейте воспользоваться предложением — акция ограничена по времени и действует только в будни.",
    "Ваш любимый кофе ещё доступнее: скидка действует при предъявлении промокода на кассе.",
  ],
  discount: ["−20%", "−15%", "2×1", "−25%"],
  code: ["HAPPY20", "COFFEE20", "BOOST15", "BEAN25"],
  headline: ["Счастливые часы", "Кофе-пауза со скидкой", "Ваш перерыв стал выгоднее"],
  subheadline: ["−20% на всё меню", "Второй напиток в подарок", "Выгода до конца месяца"],
  body: [
    "Заходите с 15:00 до 17:00 — готовим ваш любимый напиток со скидкой и всегда рады гостям ☕",
    "Тёплый свет, аромат свежей обжарки и приятная цена. Успейте до конца недели!",
  ],
  banner: ["/content/latteart.jpg", "/content/drinks.jpg", "/content/interior.jpg", "/content/newdrink.jpg"],
};

const nextOf = (arr: string[], cur: string) => {
  const i = arr.indexOf(cur);
  return arr[i >= 0 ? (i + 1) % arr.length : 0];
};

export default function PromoEditView({ promo }: { promo: Promo }) {
  const router = useRouter();

  const [tab, setTab] = useState<TabId>("info");
  const [draft, setDraft] = useState<PromoDraft>(() => draftFromPromo(promo));
  const [busy, setBusy] = useState<string | null>(null);
  const [aiOpen, setAiOpen] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  // Ссылка из карточки может вести сразу в статистику: /dashboard/promos/pr1?tab=stats
  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get("tab");
    /* eslint-disable react-hooks/set-state-in-effect */
    if (TABS.some((x) => x.id === t)) setTab(t as TabId);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  const set = <K extends keyof PromoDraft>(key: K, value: PromoDraft[K]) =>
    setDraft((d) => ({ ...d, [key]: value }));

  const period = useMemo(() => fmtPeriod(draft.dateFrom, draft.dateTo), [draft.dateFrom, draft.dateTo]);
  const pct = promoProgress(promo);

  /** Мок-генерация: короткое состояние «Генерирую…», затем плавная подстановка. */
  const generate = (key: string, ms: number, apply: () => void) => {
    setBusy(key);
    setTimeout(() => {
      apply();
      setBusy(null);
    }, ms);
  };

  const runAi = (key: AiKey) => {
    switch (key) {
      case "title": return generate(key, 700, () => set("title", nextOf(VARIANTS.title, draft.title)));
      case "description": return generate(key, 900, () => set("description", nextOf(VARIANTS.description, draft.description)));
      case "discount": return generate(key, 500, () => set("discount", nextOf(VARIANTS.discount, draft.discount)));
      case "code": return generate(key, 500, () => { set("hasCode", true); set("code", nextOf(VARIANTS.code, draft.code)); });
      case "headline": return generate(key, 700, () => set("headline", nextOf(VARIANTS.headline, draft.headline)));
      case "subheadline": return generate(key, 700, () => set("subheadline", nextOf(VARIANTS.subheadline, draft.subheadline)));
      case "body": return generate(key, 1000, () => set("bodyText", nextOf(VARIANTS.body, draft.bodyText)));
      case "banner": return generate(key, 1100, () => set("image", nextOf(VARIANTS.banner, draft.image ?? "")));
    }
  };

  /** Сценарии из панели помощника. */
  const runSuggestion = (id: string) => {
    switch (id) {
      case "headline":
        return generate(id, 700, () => { set("headline", nextOf(VARIANTS.headline, draft.headline)); setTab("content"); });
      case "description":
        return generate(id, 900, () => { set("description", nextOf(VARIANTS.description, draft.description)); setTab("info"); });
      case "attractive":
        return generate(id, 1000, () => {
          set("discount", nextOf(VARIANTS.discount, draft.discount));
          set("subheadline", nextOf(VARIANTS.subheadline, draft.subheadline));
          toast("Оффер усилен — проверьте формулировки");
        });
      case "banner":
        return generate(id, 1100, () => { set("image", nextOf(VARIANTS.banner, draft.image ?? "")); setTab("content"); });
      case "code":
        return generate(id, 600, () => { set("hasCode", true); set("code", nextOf(VARIANTS.code, draft.code)); setTab("info"); });
      case "post":
        return generate(id, 1000, () => { set("bodyText", nextOf(VARIANTS.body, draft.bodyText)); setTab("content"); toast("Пост готов — загляните во вкладку «Контент»"); });
      case "mailing":
        return generate(id, 1000, () => toast("Черновик рассылки сохранён"));
      case "stories":
        return generate(id, 1000, () => toast("Stories собраны — найдёте их в медиатеке"));
      default:
        return;
    }
  };

  const back = () => router.push("/dashboard/promos");
  const save = () => { toast("Изменения сохранены"); back(); };
  const duplicate = () => { toast("Копия создана — черновик в списке акций"); back(); };
  const remove = () => { setConfirmDelete(false); toast(`Акция «${promo.title}» удалена`); back(); };

  const tabProps = { draft, set, aiBusy: busy as AiKey | null, runAi };
  const wide = tab === "stats" || tab === "content";

  return (
    <div className="flex flex-col gap-5 pb-24">
      {/* Шапка */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={back}
          aria-label="Назад к акциям"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-ink-muted transition duration-200 hover:bg-surface-soft hover:text-ink"
        >
          <Icon name="arrow-left" size={18} aria-hidden="true" />
        </button>

        <div className="min-w-0 flex-1">
          <h1 className="truncate text-lg font-bold text-ink sm:text-xl">{draft.title || "Новая акция"}</h1>
          <p className="mt-0.5 flex items-center gap-2 text-sm text-ink-muted">
            <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[draft.status]}`} aria-hidden="true" />
            {PROMO_STATUS_LABEL[draft.status]} · {period || "период не задан"}
          </p>
        </div>

        <button
          type="button"
          onClick={() => setAiOpen((v) => !v)}
          aria-expanded={aiOpen}
          className={`inline-flex shrink-0 items-center gap-2 rounded-full border px-3.5 py-2 text-sm font-semibold transition duration-200 ${
            aiOpen ? "border-brand bg-brand/12 text-brand" : "border-brand/30 bg-brand/5 text-brand hover:bg-brand/10"
          }`}
        >
          <Icon name="sparkles" size={15} aria-hidden="true" />
          <span className="hidden sm:inline">AI-помощник</span>
        </button>
      </div>

      {/* Вкладки */}
      <div role="tablist" aria-label="Разделы акции" className="flex items-center gap-1 overflow-x-auto border-b border-border/70 pb-px">
        {TABS.map((t) => {
          const on = t.id === tab;
          return (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={on}
              onClick={() => setTab(t.id)}
              className={`relative inline-flex shrink-0 items-center gap-2 px-3.5 py-2.5 text-sm font-medium transition duration-200 ${
                on ? "text-ink" : "text-ink-muted hover:text-ink"
              }`}
            >
              <Icon name={t.icon} size={15} aria-hidden="true" />
              {t.label}
              {on && <span className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-brand" aria-hidden="true" />}
            </button>
          );
        })}
      </div>

      <div className={`grid grid-cols-1 gap-4 ${aiOpen ? "xl:grid-cols-[minmax(0,1fr)_18rem]" : ""}`}>
        <div className="min-w-0">
          <div className={`grid grid-cols-1 gap-4 ${wide ? "" : "xl:grid-cols-[minmax(0,1fr)_20rem]"}`}>
            <div key={tab} className="uc-tab-in min-w-0">
              {tab === "info" && <InfoTab {...tabProps} />}
              {tab === "mechanics" && <MechanicsTab {...tabProps} />}
              {tab === "content" && <ContentTab {...tabProps} />}
              {tab === "publish" && (
                <PublishTab
                  {...tabProps}
                  onPublish={() => { toast("Акция опубликована"); back(); }}
                  onSchedule={() => { toast("Публикация запланирована"); back(); }}
                />
              )}
              {tab === "stats" && <StatsTab promo={promo} draft={draft} />}
            </div>

            {/* Правая колонка: только предпросмотр и статус */}
            {!wide && (
              <aside className="flex min-w-0 flex-col gap-4 xl:sticky xl:top-4 xl:h-fit">
                <div>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-ink-muted">Предпросмотр</p>
                  <PromoPreview
                    title={draft.title}
                    description={draft.description}
                    discount={draft.discount || undefined}
                    code={draft.hasCode ? draft.code : undefined}
                    image={draft.image}
                    type={draft.type}
                    goal={draft.goal ? Number(draft.goal) : undefined}
                    period={period}
                    channels={draft.channels}
                    status={draft.status}
                  />
                </div>

                <Card>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm text-ink-muted">Статус</span>
                    <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-ink">
                      <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[draft.status]}`} aria-hidden="true" />
                      {PROMO_STATUS_LABEL[draft.status]}
                    </span>
                  </div>

                  <div className="mt-4 flex items-end justify-between gap-2">
                    <span className="text-sm text-ink-muted">Использований</span>
                    <span className="font-display text-2xl font-extrabold leading-none tabular-nums text-ink">
                      {fmtNum(promo.uses ?? 0)}
                    </span>
                  </div>

                  {pct !== null && (
                    <div className="mt-3">
                      <div className="h-1.5 overflow-hidden rounded-full bg-border/70">
                        <div className="uc-bar-fill h-full rounded-full bg-success" style={{ width: `${pct}%` }} />
                      </div>
                      <p className="mt-1.5 text-right text-xs tabular-nums text-ink-muted">{pct}% от цели</p>
                    </div>
                  )}

                  <button
                    type="button"
                    onClick={() => {
                      const next: PromoStatus = draft.status === "finished" ? "active" : "finished";
                      set("status", next);
                      toast(next === "finished" ? "Акция завершена" : "Акция снова активна");
                    }}
                    className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-full border border-border px-4 py-2.5 text-sm font-medium text-ink transition duration-200 hover:bg-surface-soft"
                  >
                    <Icon name={draft.status === "finished" ? "play" : "check"} size={15} aria-hidden="true" />
                    {draft.status === "finished" ? "Возобновить" : "Завершить акцию"}
                  </button>
                </Card>
              </aside>
            )}
          </div>
        </div>

        <AiSidebar open={aiOpen} onClose={() => setAiOpen(false)} busy={busy} onRun={runSuggestion} />
      </div>

      {/* Действия всегда на виду */}
      <div className="sticky bottom-3 z-30 mt-2 flex items-center gap-2 rounded-2xl border border-border/70 bg-card/85 px-4 py-3 shadow-lift backdrop-blur-xl">
        <button
          type="button"
          onClick={() => setConfirmDelete(true)}
          className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-medium text-[#e5484d] transition duration-200 hover:bg-[#e5484d]/10"
        >
          <Icon name="trash" size={15} aria-hidden="true" />
          <span className="hidden sm:inline">Удалить</span>
        </button>
        <button
          type="button"
          onClick={duplicate}
          className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-medium text-ink-muted transition duration-200 hover:bg-surface-soft hover:text-ink"
        >
          <Icon name="copy" size={15} aria-hidden="true" />
          <span className="hidden sm:inline">Дублировать</span>
        </button>

        <div className="ml-auto flex items-center gap-2">
          <button
            type="button"
            onClick={back}
            className="rounded-full px-4 py-2 text-sm font-medium text-ink-muted transition duration-200 hover:bg-surface-soft hover:text-ink"
          >
            Отмена
          </button>
          <button type="button" onClick={save} className="btn-glass-blue inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold">
            Сохранить
          </button>
        </div>
      </div>

      <ModalShell open={confirmDelete} onClose={() => setConfirmDelete(false)} labelledBy="del-promo-title">
        <div className="flex flex-col items-center text-center">
          <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[#e5484d]/12 text-[#e5484d]">
            <Icon name="trash" size={26} aria-hidden="true" />
          </span>
          <h2 id="del-promo-title" className="text-lg font-bold text-ink">Удалить акцию?</h2>
          <p className="mt-1.5 text-sm text-ink-muted">
            Акция «{draft.title}» и её статистика будут удалены безвозвратно.
          </p>
          <div className="mt-6 flex w-full flex-col gap-2 sm:flex-row-reverse">
            <button
              type="button"
              onClick={remove}
              className="inline-flex flex-1 items-center justify-center gap-2 rounded-full bg-[#e5484d] px-5 py-3 text-sm font-semibold text-white transition hover:brightness-110"
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
