"use client";

import { useState } from "react";
import Image from "next/image";
import { Sparkles, BrainCircuit, ImageIcon, CalendarPlus, Send, RefreshCw } from "lucide-react";
import { CHANNELS, CHANNEL_ORDER, type ChannelId } from "@/lib/channels";

const POST_TYPES = ["Пост", "Акция", "Анонс", "Сторис"] as const;
const LENGTHS = ["Короткий", "Средний", "Длинный"] as const;
const TONES = ["Дружелюбный", "Тёплый", "С заботой", "Экспертный"];

type PostTypeOption = (typeof POST_TYPES)[number];
type LengthOption = (typeof LENGTHS)[number];

function generateText(topic: string, type: PostTypeOption, tone: string): string {
  const subject = topic.trim() || "нашей новинке";
  const opener =
    type === "Акция"
      ? "🎉 Только сегодня — специальное предложение!"
      : type === "Анонс"
        ? "📢 У нас важная новость!"
        : "☕ Доброе утро, друзья!";
  return `${opener}\n\nРассказываем о ${subject.toLowerCase()}. Мы готовили это с заботой о вас — заходите попробовать и поделитесь впечатлениями.\n\nЖдём вас в гости! (${tone.toLowerCase()} тон)\n\n#ucust #нашбренд #${subject.replace(/\s+/g, "").toLowerCase()}`;
}

export default function CreateView() {
  const [topic, setTopic] = useState("");
  const [type, setType] = useState<PostTypeOption>("Пост");
  const [tone, setTone] = useState(TONES[0]);
  const [length, setLength] = useState<LengthOption>("Средний");
  const [channels, setChannels] = useState<ChannelId[]>(["vk", "telegram"]);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const toggleChannel = (id: ChannelId) =>
    setChannels((prev) => (prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]));

  const generate = () => {
    setGenerating(true);
    setResult(null);
    setTimeout(() => {
      setResult(generateText(topic, type, tone));
      setGenerating(false);
    }, 1100);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink sm:text-3xl">Создать контент</h1>
          <p className="mt-1 text-sm text-ink-muted">AI сгенерирует пост под ваш бренд</p>
        </div>
        <span className="inline-flex items-center gap-1.5 self-start rounded-full bg-brand-tint px-3 py-1.5 text-xs font-medium text-brand">
          <BrainCircuit size={14} aria-hidden="true" /> Использует мозг бренда
        </span>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Бриф */}
        <div className="flex flex-col gap-5 rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
          <label className="block">
            <span className="mb-1.5 block text-sm font-semibold text-ink">О чём пост?</span>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Например: новое сезонное меню, скидка на завтраки, история бренда"
              className="min-h-24 w-full resize-none rounded-xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition focus:border-brand focus:ring-2 focus:ring-brand-tint"
            />
          </label>

          <div>
            <span className="mb-1.5 block text-sm font-semibold text-ink">Тип</span>
            <div className="flex flex-wrap gap-2">
              {POST_TYPES.map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setType(t)}
                  className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
                    type === t ? "bg-brand text-white" : "bg-surface-soft text-ink hover:text-brand"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div>
            <span className="mb-1.5 block text-sm font-semibold text-ink">Тон <span className="font-normal text-ink-muted">(из голоса бренда)</span></span>
            <div className="flex flex-wrap gap-2">
              {TONES.map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setTone(t)}
                  className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
                    tone === t ? "bg-brand/12 text-brand ring-1 ring-brand" : "bg-surface-soft text-ink-muted hover:text-ink"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div>
            <span className="mb-1.5 block text-sm font-semibold text-ink">Длина</span>
            <div className="flex gap-2">
              {LENGTHS.map((l) => (
                <button
                  key={l}
                  type="button"
                  onClick={() => setLength(l)}
                  className={`flex-1 rounded-xl px-3 py-2 text-sm font-medium transition ${
                    length === l ? "bg-brand text-white" : "bg-surface-soft text-ink hover:text-brand"
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>

          <div>
            <span className="mb-1.5 block text-sm font-semibold text-ink">Каналы</span>
            <div className="flex flex-wrap gap-2">
              {CHANNEL_ORDER.slice(0, 6).map((id) => {
                const ch = CHANNELS[id];
                const on = channels.includes(id);
                return (
                  <button
                    key={id}
                    type="button"
                    aria-pressed={on}
                    onClick={() => toggleChannel(id)}
                    className={`inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition ${
                      on ? "border-brand bg-brand/8 text-ink" : "border-border bg-surface-soft text-ink-muted"
                    }`}
                  >
                    {ch.icon && ch.iconType !== "wordmark" ? (
                      <Image src={ch.icon} alt="" width={18} height={18} className="h-[18px] w-[18px] object-contain" aria-hidden="true" />
                    ) : (
                      <span className="h-[18px] w-[18px] rounded" style={{ backgroundColor: ch.colorVar }} aria-hidden="true" />
                    )}
                    {ch.label}
                  </button>
                );
              })}
            </div>
          </div>

          <button
            type="button"
            onClick={generate}
            disabled={generating}
            className="btn-glass-blue inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3.5 text-sm font-semibold disabled:opacity-60"
          >
            {generating ? <RefreshCw size={16} className="animate-spin" aria-hidden="true" /> : <Sparkles size={16} aria-hidden="true" />}
            {generating ? "Генерируем…" : "Сгенерировать"}
          </button>
        </div>

        {/* Превью */}
        <div className="rounded-[24px] border border-border bg-card p-5 shadow-soft sm:p-6">
          {!result && !generating && (
            <div className="grid h-full min-h-72 place-items-center text-center">
              <div className="text-ink-muted">
                <Sparkles size={28} className="mx-auto mb-3 text-brand/60" aria-hidden="true" />
                <p className="text-sm">Заполните бриф и нажмите «Сгенерировать» —<br />здесь появится готовый пост</p>
              </div>
            </div>
          )}

          {generating && (
            <div className="flex flex-col gap-3">
              <div className="h-40 animate-pulse rounded-2xl bg-surface-soft" />
              <div className="h-3 w-3/4 animate-pulse rounded bg-surface-soft" />
              <div className="h-3 w-full animate-pulse rounded bg-surface-soft" />
              <div className="h-3 w-2/3 animate-pulse rounded bg-surface-soft" />
            </div>
          )}

          {result && (
            <div className="flex flex-col gap-4">
              <div className="overflow-hidden rounded-2xl border border-border">
                <div className="flex items-center gap-2.5 border-b border-border bg-surface-soft px-4 py-3">
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-brand text-sm font-semibold text-white">UC</span>
                  <span className="leading-tight">
                    <span className="block text-sm font-semibold text-ink">Ваш бизнес</span>
                    <span className="block text-xs text-ink-muted">только что</span>
                  </span>
                </div>
                <div className="grid h-44 place-items-center bg-gradient-to-br from-surface-blue via-surface-soft to-surface-blue text-ink-muted">
                  <span className="inline-flex items-center gap-2 text-sm"><ImageIcon size={18} aria-hidden="true" /> Изображение поста</span>
                </div>
                <textarea
                  value={result}
                  onChange={(e) => setResult(e.target.value)}
                  className="min-h-44 w-full resize-none border-0 bg-card px-4 py-3 text-sm leading-relaxed text-ink outline-none"
                />
              </div>

              <div className="flex flex-wrap gap-2">
                <button type="button" className="btn-glass-blue inline-flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold">
                  <CalendarPlus size={16} aria-hidden="true" /> Запланировать
                </button>
                <button type="button" className="btn-glass inline-flex flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold">
                  <Send size={16} aria-hidden="true" /> Опубликовать
                </button>
                <button type="button" onClick={generate} aria-label="Перегенерировать" className="btn-glass inline-flex items-center justify-center rounded-xl px-4 py-3">
                  <RefreshCw size={16} aria-hidden="true" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
