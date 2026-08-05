"use client";

import { useEffect, useRef, useState, type ChangeEvent } from "react";
import { createPortal } from "react-dom";
import Image from "next/image";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import EmojiPicker from "@/components/ui/EmojiPicker";
import { toast } from "@/lib/toast";
import { CHANNELS, CHANNEL_ORDER, type ChannelId } from "@/lib/channels";
import PromoPreview from "@/components/dashboard/promos/PromoPreview";
import PromptComposer from "@/components/dashboard/PromptComposer";
import { useAttachments } from "@/lib/dashboard/attachments";
import {
  PROMO_IMAGE_POOL,
  PROMO_TYPE,
  PROMO_TYPE_ORDER,
  type PromoType,
} from "@/lib/dashboard/promos";

type Step = "brief" | "generating" | "result";

const STEP_ORDER: Step[] = ["brief", "generating", "result"];
const STEP_LABELS = ["Идея", "Генерация", "Запуск"];

const PHOTO_STEP = "Смотрим, что на фото";
const AI_STEPS = [
  "Анализируем бренд и аудиторию",
  "Подбираем механику акции",
  "Формулируем оффер",
  "Пишем описание и промокод",
  "Готовим обложку",
];

/* Подсказки-идеи: клик подставляет готовый бриф и механику. */
const IDEAS: { label: string; text: string; type: PromoType }[] = [
  { label: "Скидка в тихие часы",   type: "discount", text: "Скидка 20% на все напитки по будням с 15:00 до 17:00 — хочу загрузить тихое время." },
  { label: "2 по цене 1",           type: "gift",     text: "При покупке любого напитка второй в подарок, по выходным." },
  { label: "Подарок новому гостю",  type: "gift",     text: "Десерт в подарок новым гостям, которые пришли впервые по нашему посту." },
  { label: "День рождения",         type: "event",    text: "Отмечаем день рождения кофейни: праздничное меню, угощения и розыгрыш сертификатов." },
  { label: "Промокод подписчикам",  type: "code",     text: "Промокод со скидкой 15% для подписчиков наших соцсетей, на любой заказ." },
  { label: "Сезонное предложение",  type: "discount", text: "Сезонное предложение на новинки меню — действует месяц." },
];

/* Мок-генерация: заготовка подбирается по ключевым словам брифа. */
const AI_BRIEF: Record<string, { title: string; discount: string; description: string; code: string }> = {
  скид:     { title: "Скидка на все напитки",   discount: "−20%", description: "Горячие и холодные напитки со скидкой 20% каждый будний день с 15:00 до 17:00. Успейте зайти в перерыве.", code: "HAPPY20" },
  подар:    { title: "Второй кофе в подарок",   discount: "2×1",  description: "Купите один напиток — второй бесплатно. Предложение действует по выходным, весь день.", code: "" },
  десерт:   { title: "Десерт новому гостю",     discount: "🎁",   description: "Первый визит — приятный бонус: десерт в подарок к любому напитку. Покажите этот пост на кассе.", code: "WELCOME" },
  рожден:   { title: "День рождения кофейни",   discount: "🎂",   description: "Отмечаем день рождения! Праздничное меню, угощения и розыгрыш подарочных сертификатов — весь день.", code: "BDAY" },
  промокод: { title: "Специальное предложение", discount: "−15%", description: "Используйте промокод и получите скидку на любой заказ — для подписчиков наших соцсетей.", code: "COFFEE15" },
  сезон:    { title: "Сезонные новинки",        discount: "−15%", description: "Новинки сезона по специальной цене: пробуйте авторские напитки, пока предложение действует.", code: "SEASON15" },
};

function generateFromBrief(brief: string, type: PromoType, photoCount = 0) {
  const lower = brief.toLowerCase();
  const key = Object.keys(AI_BRIEF).find((k) => lower.includes(k));
  const preset = AI_BRIEF[key ?? "скид"];
  const typeHint = PROMO_TYPE[type].hint;
  return {
    title: preset.title,
    discount: typeHint || preset.discount,
    description: photoCount
      ? `${preset.description} На фото — то, что участвует в акции.`
      : preset.description,
    code: type === "code" ? preset.code || "PROMO15" : preset.code,
    image: PROMO_IMAGE_POOL[Math.floor(Math.random() * PROMO_IMAGE_POOL.length)],
  };
}

const MONTHS_GEN = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"];
const fmtDate = (iso: string) => {
  if (!iso) return "—";
  const [y, m, d] = iso.split("-");
  return `${+d} ${MONTHS_GEN[+m - 1] ?? ""}`.trim() || y;
};
const isoOffset = (days: number) => {
  const t = new Date();
  t.setDate(t.getDate() + days);
  return t.toISOString().slice(0, 10);
};

const channelIcon = (id: ChannelId, size = 16) => {
  const ch = CHANNELS[id];
  return ch.icon && ch.iconType !== "wordmark" ? (
    <Image key={id} src={ch.icon} alt="" width={size} height={size} style={{ width: size, height: size }} className="object-contain" aria-hidden="true" />
  ) : (
    <span key={id} className="rounded-full" style={{ width: size, height: size, backgroundColor: ch.colorVar }} aria-hidden="true" />
  );
};

/* ── Скелет карточки на время генерации ── */
function GeneratingSkeleton() {
  return (
    <div className="overflow-hidden rounded-[24px] border border-border bg-card">
      <div className="h-40 animate-pulse bg-surface-soft" />
      <div className="flex flex-col gap-3 p-5">
        <div className="h-4 w-2/3 animate-pulse rounded-full bg-surface-soft" />
        <div className="h-3 w-full animate-pulse rounded-full bg-surface-soft" />
        <div className="h-3 w-3/4 animate-pulse rounded-full bg-surface-soft" />
      </div>
    </div>
  );
}

export default function PromoCreateView() {
  const router = useRouter();

  const [step, setStep] = useState<Step>("brief");
  const [doneSteps, setDoneSteps] = useState(0);

  /* Бриф */
  const [brief, setBrief]       = useState("");
  const [type, setType]         = useState<PromoType>("discount");
  const [channels, setChannels] = useState<ChannelId[]>(["vk", "telegram"]);
  const [goal, setGoal]         = useState("");
  const photos = useAttachments(); // фото к брифу — контекст для ИИ

  /* Результат */
  const [title, setTitle]             = useState("");
  const [discount, setDiscount]       = useState("");
  const [description, setDescription] = useState("");
  const [code, setCode]               = useState("");
  const [hasCode, setHasCode]         = useState(false);
  const [image, setImage]             = useState<string | undefined>(undefined);

  const [launchMode, setLaunchMode] = useState<null | "launch" | "schedule">(null);

  const fileInput  = useRef<HTMLInputElement>(null);
  const descriptionRef = useRef<HTMLTextAreaElement>(null);
  const objectUrls = useRef<string[]>([]);
  const timer      = useRef<ReturnType<typeof setInterval> | null>(null);
  useEffect(() => () => {
    objectUrls.current.forEach((u) => URL.revokeObjectURL(u));
    if (timer.current) clearInterval(timer.current);
  }, []);

  const aiSteps = photos.items.length > 0 ? [PHOTO_STEP, ...AI_STEPS] : AI_STEPS;
  const canGenerate = brief.trim().length > 0 || photos.items.length > 0;

  const generate = () => {
    if (!canGenerate) return;
    setStep("generating");
    setDoneSteps(0);
    let done = 0;
    if (timer.current) clearInterval(timer.current);
    timer.current = setInterval(() => {
      done += 1;
      setDoneSteps(done);
      if (done >= aiSteps.length) {
        if (timer.current) clearInterval(timer.current);
        setTimeout(() => {
          const g = generateFromBrief(brief, type, photos.items.length);
          setTitle(g.title);
          setDiscount(g.discount);
          setDescription(g.description);
          setCode(g.code);
          setHasCode(!!g.code);
          setImage(g.image);
          setStep("result");
        }, 420);
      }
    }, 480);
  };

  const onFile = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) { const u = URL.createObjectURL(f); objectUrls.current.push(u); setImage(u); }
    e.target.value = "";
  };

  const saveDraft = () => { toast("Акция сохранена в черновики"); router.push("/dashboard/promos"); };
  const restart = () => { setStep("brief"); setDoneSteps(0); };

  const inputClass =
    "w-full rounded-xl border border-border bg-surface-soft px-4 py-2.5 text-sm text-ink outline-none transition focus:border-brand focus:ring-1 focus:ring-brand/25 placeholder:text-ink-muted/60";

  const curStep = STEP_ORDER.indexOf(step);

  return (
    <div className="flex flex-col gap-6 lg:min-h-[calc(100dvh-150px)]">
      {/* Шапка */}
      <div className="flex items-start gap-3 border-b border-border pb-4">
        <button
          type="button"
          onClick={() => router.push("/dashboard/promos")}
          aria-label="Назад к акциям"
          className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-border bg-card text-ink-muted transition hover:text-ink"
        >
          <Icon name="arrow-left" size={18} aria-hidden="true" />
        </button>
        <div className="min-w-0">
          <h1 className="text-xl font-bold text-ink sm:text-2xl">Новая акция</h1>
          {step === "result" ? (
            <p className="mt-1 inline-flex items-center gap-2 text-sm text-success">
              <Icon name="check-bold" size={16} aria-hidden="true" /> Акция готова — проверьте детали
            </p>
          ) : (
            <p className="mt-0.5 text-sm text-ink-muted">
              Опишите идею. Оффер, описание и промокод UCust придумает сам.
            </p>
          )}
        </div>
      </div>

      {/* Прогресс шагов */}
      <ol className="flex flex-wrap items-center gap-x-3 gap-y-2 text-xs font-medium">
        {STEP_ORDER.map((s, i) => {
          const done = i < curStep;
          const active = i === curStep;
          return (
            <li key={s} className="flex items-center gap-2">
              <span
                className={`flex h-5 w-5 items-center justify-center rounded-full text-[0.625rem] font-bold ${
                  done ? "bg-success text-white" : active ? "bg-brand text-white" : "bg-surface-soft text-ink-muted"
                }`}
              >
                {done ? <Icon name="check" size={11} aria-hidden="true" /> : i + 1}
              </span>
              <span className={done || active ? "text-ink" : "text-ink-muted"}>{STEP_LABELS[i]}</span>
              {i < STEP_ORDER.length - 1 && <span className="ml-1 h-px w-6 bg-border sm:w-10" aria-hidden="true" />}
            </li>
          );
        })}
      </ol>

      <div className="grid grid-cols-1 gap-8 lg:min-h-0 lg:flex-1 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
        {/* ══ ЛЕВО: бриф и настройки ══ */}
        <div className="flex flex-col gap-6">
          {step === "result" ? (
            <div className="uc-fade-in flex flex-col gap-5">
              <div className="flex flex-col gap-1.5">
                <span className="mb-1 text-xs font-semibold uppercase tracking-wider text-ink-muted">Действия</span>
                <button type="button" onClick={restart} className="flex items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm font-medium text-ink transition hover:bg-surface-soft">
                  <Icon name="edit" size={17} className="text-ink-muted" aria-hidden="true" /> Изменить запрос
                </button>
                <button type="button" onClick={generate} className="flex items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm font-medium text-ink transition hover:bg-surface-soft">
                  <Icon name="refresh" size={17} className="text-ink-muted" aria-hidden="true" /> Сгенерировать заново
                </button>
                <button type="button" onClick={saveDraft} className="flex items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm font-medium text-ink transition hover:bg-surface-soft">
                  <Icon name="file-text" size={17} className="text-ink-muted" aria-hidden="true" /> Сохранить в черновики
                </button>
              </div>

              <div className="rounded-2xl border border-border bg-card p-4">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-ink-muted">Ваш запрос</p>
                <p className="text-sm leading-relaxed text-ink-muted">{brief}</p>
              </div>
            </div>
          ) : (
            <>
              <PromptComposer
                value={brief}
                onChange={setBrief}
                placeholder="Например: скидка 20% на горячие напитки по будням с 15:00 до 17:00, промокод HAPPY20, цель — 300 использований."
                attachments={photos.items}
                onAttach={photos.add}
                onRemove={photos.remove}
                max={photos.max}
                disabled={step === "generating"}
                autoFocus
                onSubmit={generate}
                footer="Можно приложить фото — ИИ учтёт их в описании"
              />

              {step === "brief" && (
                <>
                  <div>
                    <span className="mb-2 block text-sm font-medium text-ink-muted">С чего начать</span>
                    <div className="flex flex-wrap gap-2">
                      {IDEAS.map((idea) => (
                        <button
                          key={idea.label}
                          type="button"
                          onClick={() => { setBrief(idea.text); setType(idea.type); }}
                          className="rounded-full border border-border bg-transparent px-4 py-2 text-sm font-medium text-ink-muted transition hover:border-brand/40 hover:text-ink"
                        >
                          {idea.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="mb-2.5 block text-sm font-medium text-ink-muted">Механика</span>
                    <div className="grid grid-cols-4 gap-2">
                      {PROMO_TYPE_ORDER.map((t) => {
                        const meta = PROMO_TYPE[t];
                        const on = type === t;
                        return (
                          <button
                            key={t}
                            type="button"
                            aria-pressed={on}
                            onClick={() => setType(t)}
                            className={`flex flex-col items-center gap-1.5 rounded-xl border px-3 py-3 text-xs font-medium transition ${
                              on ? "border-brand bg-brand/8 text-brand" : "border-border bg-surface-soft text-ink-muted hover:text-ink"
                            }`}
                          >
                            <Icon name={meta.icon} size={18} aria-hidden="true" />
                            {meta.label}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div>
                    <span className="mb-2.5 block text-sm font-medium text-ink-muted">Цель по использованиям</span>
                    <div className="flex flex-wrap items-center gap-3">
                      <input
                        type="number"
                        min={1}
                        value={goal}
                        onChange={(e) => setGoal(e.target.value)}
                        placeholder="300"
                        className={`${inputClass} w-32`}
                      />
                      <span className="text-xs text-ink-muted">необязательно — покажем прогресс на карточке</span>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={generate}
                    disabled={!canGenerate}
                    className="btn-glass-blue mt-1 inline-flex items-center justify-center gap-2 px-6 py-4 text-base font-semibold disabled:cursor-not-allowed disabled:opacity-50 lg:mt-auto"
                  >
                    <Icon name="sparkles" size={18} aria-hidden="true" /> Создать акцию
                  </button>
                  {!canGenerate && (
                    <p className="-mt-4 text-xs text-ink-muted">
                      Опишите акцию в одном-двух предложениях — этого достаточно. Ctrl+Enter — сгенерировать.
                    </p>
                  )}
                </>
              )}
            </>
          )}
          <input ref={fileInput} type="file" accept="image/*" hidden onChange={onFile} />
        </div>

        {/* ══ ПРАВО: превью и правка ══ */}
        <div className="flex min-h-0 flex-col">
          {step === "result" ? (
            <div className="uc-fade-in flex flex-col gap-5 rounded-[28px] border border-border bg-card p-5 sm:p-6">
              <PromoPreview
                title={title}
                description={description}
                discount={discount}
                code={hasCode ? code : undefined}
                image={image}
                type={type}
                goal={goal ? Number(goal) : undefined}
                channels={channels}
                status="active"
              />

              <div className="flex flex-col gap-4 border-t border-border pt-5">
                <p className="text-sm font-semibold text-ink">Подправить вручную</p>

                <label className="block">
                  <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">Название</span>
                  <input value={title} onChange={(e) => setTitle(e.target.value)} className={inputClass} />
                </label>

                <label className="block">
                  <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">Предложение</span>
                  <input
                    value={discount}
                    onChange={(e) => setDiscount(e.target.value)}
                    placeholder="−20%, 2×1, 🎂…"
                    className={`${inputClass} font-display text-2xl font-bold`}
                  />
                </label>

                <div>
                  <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">Описание</span>
                  {/* Счётчик слева, эмодзи в самом поле — как в редакторе публикации */}
                  <div className="rounded-xl border border-border bg-surface-soft transition focus-within:border-brand focus-within:ring-1 focus-within:ring-brand/25">
                    <textarea
                      ref={descriptionRef}
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      rows={3}
                      className="w-full resize-none bg-transparent px-4 pt-2.5 text-sm text-ink outline-none placeholder:text-ink-muted/60"
                    />
                    <div className="flex items-center justify-between gap-2 px-3 pb-2">
                      <span className="text-xs text-ink-muted/70">{description.length} символов</span>
                      <EmojiPicker targetRef={descriptionRef} value={description} onChange={setDescription} />
                    </div>
                  </div>
                </div>

                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wider text-ink-muted">Промокод</span>
                    <button
                      type="button"
                      onClick={() => setHasCode((v) => !v)}
                      aria-pressed={hasCode}
                      aria-label="Промокод в акции"
                      className={`relative inline-flex h-5 w-9 shrink-0 rounded-full transition-colors ${hasCode ? "bg-brand" : "bg-border"}`}
                    >
                      <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${hasCode ? "translate-x-4" : "translate-x-0.5"}`} />
                    </button>
                  </div>
                  {hasCode && (
                    <input
                      value={code}
                      onChange={(e) => setCode(e.target.value.toUpperCase())}
                      placeholder="PROMO25"
                      className={`${inputClass} font-mono font-bold uppercase tracking-widest placeholder:font-normal placeholder:normal-case placeholder:tracking-normal`}
                    />
                  )}
                </div>

                <div>
                  <span className="mb-2 block text-xs font-semibold uppercase tracking-wider text-ink-muted">Обложка</span>
                  <div className="flex flex-wrap items-center gap-3">
                    <div className={`relative h-16 w-24 shrink-0 overflow-hidden rounded-xl border border-border ${image ? "" : `grid place-items-center bg-gradient-to-br ${PROMO_TYPE[type].cover}`}`}>
                      {image ? (
                        <Image src={image} alt="" fill className="object-cover" unoptimized={image.startsWith("blob:")} sizes="96px" />
                      ) : (
                        <Icon name={PROMO_TYPE[type].icon} size={20} aria-hidden="true" />
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => setImage(PROMO_IMAGE_POOL[(image ? PROMO_IMAGE_POOL.indexOf(image) + 1 : 0) % PROMO_IMAGE_POOL.length])}
                        className="btn-glass inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium"
                      >
                        <Icon name="refresh" size={13} aria-hidden="true" /> Другое
                      </button>
                      <button type="button" onClick={() => fileInput.current?.click()} className="btn-glass inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium">
                        <Icon name="image-plus" size={13} aria-hidden="true" /> Загрузить
                      </button>
                      {image && (
                        <button
                          type="button"
                          onClick={() => setImage(undefined)}
                          className="inline-flex items-center gap-1.5 rounded-full px-3 py-2 text-xs font-medium text-ink-muted transition hover:text-ink"
                        >
                          <Icon name="close" size={12} aria-hidden="true" /> Без фото
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Действия */}
              <div className="flex flex-col gap-2 border-t border-border pt-4 sm:flex-row sm:items-center">
                <button type="button" onClick={() => setLaunchMode("launch")} className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 px-4 py-3 text-sm font-semibold">
                  <Icon name="play" size={16} aria-hidden="true" /> Запустить сейчас
                </button>
                <button type="button" onClick={() => setLaunchMode("schedule")} className="btn-glass inline-flex flex-1 items-center justify-center gap-2 px-4 py-3 text-sm font-semibold">
                  <Icon name="calendar-plus" size={16} aria-hidden="true" /> Запланировать
                </button>
                <button type="button" onClick={saveDraft} className="inline-flex items-center justify-center gap-2 rounded-full px-4 py-3 text-sm font-medium text-ink-muted transition hover:text-ink">
                  Черновик
                </button>
              </div>
            </div>
          ) : (
            <div className="flex min-h-[540px] flex-col rounded-[28px] border border-border bg-card p-6 sm:p-7 lg:min-h-0 lg:flex-1">
              {step === "generating" ? (
                <div className="flex flex-1 flex-col items-center justify-center gap-6 py-6 text-center">
                  <span className="flex h-16 w-16 items-center justify-center rounded-3xl bg-brand/10 text-brand">
                    <Icon name="sparkles" size={30} className="animate-pulse" aria-hidden="true" />
                  </span>
                  <div>
                    <p className="text-lg font-bold text-ink">UCust собирает акцию</p>
                    <p className="mt-1 text-sm text-ink-muted">Несколько секунд — и готово</p>
                  </div>
                  <ul className="flex w-full max-w-xs flex-col gap-3 text-left">
                    {aiSteps.map((s, i) => {
                      const done = i < doneSteps;
                      const active = i === doneSteps;
                      return (
                        <li key={s} className={`flex items-center gap-3 text-sm transition ${done || active ? "text-ink" : "text-ink-muted/50"}`}>
                          <span className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full ${done ? "bg-success text-white" : active ? "bg-brand/15 text-brand" : "bg-surface-soft text-ink-muted/50"}`}>
                            {done ? <Icon name="check" size={12} aria-hidden="true" /> : active ? <Icon name="refresh" size={12} className="animate-spin" aria-hidden="true" /> : <span className="h-1.5 w-1.5 rounded-full bg-current" />}
                          </span>
                          {s}
                        </li>
                      );
                    })}
                  </ul>
                  <div className="w-full max-w-sm"><GeneratingSkeleton /></div>
                </div>
              ) : (
                /* Плейсхолдер будущей карточки */
                <div className="flex flex-1 flex-col gap-5">
                  <div className={`grid h-56 w-full place-items-center rounded-2xl bg-surface-soft bg-gradient-to-br sm:h-64 lg:h-auto lg:flex-1 ${PROMO_TYPE[type].cover}`}>
                    <span className="flex flex-col items-center gap-2 opacity-70">
                      <Icon name={PROMO_TYPE[type].icon} size={34} aria-hidden="true" />
                      <span className="text-sm font-semibold">{PROMO_TYPE[type].label}</span>
                    </span>
                  </div>
                  <div className="flex flex-col gap-2.5">
                    <div className="h-3.5 w-3/4 rounded-full bg-surface-soft" />
                    <div className="h-3.5 w-full rounded-full bg-surface-soft" />
                    <div className="h-3.5 w-2/3 rounded-full bg-surface-soft" />
                  </div>
                  <p className="mt-auto inline-flex items-center gap-1.5 pt-4 text-sm text-ink-muted">
                    <Icon name="sparkles" size={14} className="text-brand" aria-hidden="true" /> Здесь появится готовая карточка акции
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* key сбрасывает внутреннее состояние окна при каждом открытии */}
      <LaunchFlow
        key={launchMode ?? "closed"}
        mode={launchMode}
        channels={channels}
        onChange={setChannels}
        onClose={() => setLaunchMode(null)}
        onDone={() => { setLaunchMode(null); router.push("/dashboard/promos"); }}
      />
    </div>
  );
}

/* ── Флоу запуска: каналы → период → экран успеха ── */
const CONNECTED = new Set<ChannelId>(["vk", "telegram", "max", "ok", "zen"]);

function ChannelCard({ id, on, onToggle }: { id: ChannelId; on: boolean; onToggle: () => void }) {
  const ch = CHANNELS[id];
  if (!CONNECTED.has(id)) {
    return (
      <div className="flex flex-col gap-1.5 rounded-2xl border border-dashed border-border p-3.5">
        <span className="flex items-center gap-2 text-sm font-medium text-ink-muted">{channelIcon(id, 18)} {ch.label}</span>
        <span className="text-xs text-ink-muted/70">Не подключён</span>
        <button type="button" onClick={() => toast("Подключение канала скоро появится")} className="text-left text-xs font-semibold text-brand transition hover:opacity-70">
          Подключить
        </button>
      </div>
    );
  }
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-pressed={on}
      className={`flex items-center gap-2.5 rounded-2xl border p-3.5 text-left transition ${on ? "border-brand bg-brand/8" : "border-border hover:border-brand/40"}`}
    >
      {channelIcon(id, 20)}
      <span className="min-w-0 flex-1 truncate text-sm font-medium text-ink">{ch.label}</span>
      <span className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border transition ${on ? "border-brand bg-brand text-white" : "border-border"}`}>
        {on && <Icon name="check" size={12} aria-hidden="true" />}
      </span>
    </button>
  );
}

function LaunchFlow({
  mode, channels, onChange, onClose, onDone,
}: {
  mode: null | "launch" | "schedule";
  channels: ChannelId[];
  onChange: (v: ChannelId[]) => void;
  onClose: () => void;
  onDone: () => void;
}) {
  const [stage, setStage] = useState<"form" | "done">("form");
  const [from, setFrom] = useState(isoOffset(1));
  const [to, setTo] = useState(isoOffset(15));

  useEffect(() => {
    if (!mode) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => { document.removeEventListener("keydown", onKey); document.body.style.overflow = prev; };
  }, [mode, onClose]);

  // Модалка открывается только по клику, поэтому на сервере она не рендерится
  // и SSR-заглушка не нужна — портал ставим прямо в body.
  if (!mode || typeof document === "undefined") return null;

  const isSchedule = mode === "schedule";
  const chosen = channels.filter((c) => CONNECTED.has(c));
  const toggle = (id: ChannelId) =>
    onChange(channels.includes(id) ? channels.filter((x) => x !== id) : [...channels, id]);

  return createPortal(
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="uc-fade-in absolute inset-0 bg-ink/50 backdrop-blur-sm" onClick={onClose} aria-hidden="true" />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={isSchedule ? "Запланировать акцию" : "Запустить акцию"}
        className="uc-modal-in relative flex max-h-[92vh] w-full max-w-lg flex-col overflow-hidden rounded-[28px] border border-border bg-card shadow-lift"
      >
        {stage === "form" ? (
          <>
            <div className="flex items-center justify-between border-b border-border px-5 py-4">
              <span className="text-base font-bold text-ink">{isSchedule ? "Запланировать акцию" : "Запустить акцию"}</span>
              <button type="button" onClick={onClose} aria-label="Закрыть" className="flex h-9 w-9 items-center justify-center rounded-full text-ink-muted transition hover:bg-surface-soft hover:text-ink">
                <Icon name="close" size={20} aria-hidden="true" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-5">
              <span className="mb-2.5 block text-sm font-medium text-ink-muted">Где показать акцию</span>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                {CHANNEL_ORDER.map((id) => (
                  <ChannelCard key={id} id={id} on={channels.includes(id)} onToggle={() => toggle(id)} />
                ))}
              </div>

              <div className="mt-5 grid grid-cols-2 gap-3 border-t border-border pt-5">
                <label className="block">
                  <span className="mb-1.5 block text-sm font-medium text-ink-muted">{isSchedule ? "Старт" : "Действует с"}</span>
                  <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="w-full rounded-2xl border border-transparent bg-surface-soft px-4 py-2.5 text-sm text-ink outline-none transition focus:border-brand/40" />
                </label>
                <label className="block">
                  <span className="mb-1.5 block text-sm font-medium text-ink-muted">Окончание</span>
                  <input type="date" value={to} onChange={(e) => setTo(e.target.value)} className="w-full rounded-2xl border border-transparent bg-surface-soft px-4 py-2.5 text-sm text-ink outline-none transition focus:border-brand/40" />
                </label>
              </div>

              <p className="mt-4 inline-flex items-start gap-1.5 text-xs text-ink-muted">
                <Icon name="sparkles" size={13} className="mt-px shrink-0 text-brand" aria-hidden="true" />
                Текст акции адаптируется под каждую площадку, а по окончании периода она закроется автоматически.
              </p>

              {chosen.length === 0 && (
                <p className="mt-3 text-xs font-medium text-brand-orange">
                  Выберите хотя бы одну подключённую площадку.
                </p>
              )}
            </div>

            <div className="flex items-center gap-2 border-t border-border p-4">
              <button type="button" onClick={onClose} className="inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-medium text-ink-muted transition hover:text-ink">
                Отмена
              </button>
              <button
                type="button"
                onClick={() => setStage("done")}
                disabled={chosen.length === 0}
                className="btn-glass-blue ml-auto inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Icon name={isSchedule ? "calendar-plus" : "play"} size={16} aria-hidden="true" />
                {isSchedule ? "Запланировать" : "Запустить"}
              </button>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center gap-5 px-6 py-10 text-center">
            <span className="flex h-16 w-16 items-center justify-center rounded-full bg-success/15 text-success">
              <Icon name="check-bold" size={32} aria-hidden="true" />
            </span>
            <div>
              <h2 className="text-lg font-bold text-ink">{isSchedule ? "Акция запланирована" : "Акция запущена"}</h2>
              <p className="mt-1 text-sm text-ink-muted">{fmtDate(from)} — {fmtDate(to)}</p>
            </div>
            <div className="flex flex-col gap-1.5">
              {chosen.map((id) => (
                <span key={id} className="inline-flex items-center gap-2 text-sm text-ink">
                  {channelIcon(id, 18)} {CHANNELS[id].label} <Icon name="check" size={14} className="text-success" aria-hidden="true" />
                </span>
              ))}
            </div>
            <button type="button" onClick={onDone} className="btn-glass-blue mt-2 inline-flex w-full items-center justify-center gap-2 px-5 py-3 text-sm font-semibold">
              Вернуться к акциям
            </button>
          </div>
        )}
      </div>
    </div>,
    document.body,
  );
}
