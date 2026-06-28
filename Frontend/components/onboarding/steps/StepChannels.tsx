"use client";

import { useRef, useState } from "react";
import Image from "next/image";
import { Check, ChevronDown, Upload, X } from "lucide-react";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { CHANNELS, CHANNEL_ORDER, type ChannelId, type ChannelMeta } from "@/lib/channels";

const DEFAULT_VISIBLE = 4;

function ChannelBadge({ channel }: { channel: ChannelMeta }) {
  if (channel.icon && channel.iconType !== "wordmark") {
    return (
      <span className="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-surface-soft">
        <Image src={channel.icon} alt="" width={28} height={28} className="h-7 w-7 object-contain" aria-hidden="true" />
      </span>
    );
  }
  return (
    <span
      className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-xs font-bold text-white"
      style={{ backgroundColor: channel.colorVar }}
      aria-hidden="true"
    >
      {channel.short}
    </span>
  );
}

export default function StepChannels() {
  const { input, updateInput } = useOnboarding();
  const fileRef = useRef<HTMLInputElement>(null);
  const [expanded, setExpanded] = useState(false);

  const toggle = (id: ChannelId) => {
    const connected = input.socials.includes(id);
    updateInput({ socials: connected ? input.socials.filter((s) => s !== id) : [...input.socials, id] });
  };

  const addFiles = (list: FileList | null) => {
    if (!list) return;
    const names = Array.from(list).map((f) => f.name);
    updateInput({ files: [...input.files, ...names].slice(0, 10) });
  };

  const visibleIds = expanded ? CHANNEL_ORDER : CHANNEL_ORDER.slice(0, DEFAULT_VISIBLE);
  const hiddenCount = CHANNEL_ORDER.length - DEFAULT_VISIBLE;

  return (
    <div className="flex flex-col gap-5">
      <header>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">Подключите соцсети</h1>
        <p className="mt-2 text-sm text-ink-muted sm:text-base">
          Выберите, куда будем публиковать контент. Можно пропустить и настроить позже.
        </p>
      </header>

      <div className="grid gap-3 sm:grid-cols-2">
        {visibleIds.map((id) => {
          const channel = CHANNELS[id];
          const connected = input.socials.includes(id);
          return (
            <button
              key={id}
              type="button"
              aria-pressed={connected}
              onClick={() => toggle(id)}
              className={`flex items-center gap-3 rounded-2xl border bg-card px-4 py-3.5 text-left transition ${
                connected ? "border-brand ring-1 ring-brand" : "border-border hover:border-brand/50"
              }`}
            >
              <ChannelBadge channel={channel} />
              <span className="leading-tight">
                <span className="block text-sm font-semibold text-ink">{channel.label}</span>
                <span className={`block text-xs ${connected ? "text-brand" : "text-ink-muted"}`}>
                  {connected ? "Подключено" : "Нажмите для подключения"}
                </span>
              </span>
              {connected && <Check size={18} className="ml-auto text-brand" aria-hidden="true" />}
            </button>
          );
        })}
      </div>

      {hiddenCount > 0 && (
        <button
          type="button"
          aria-expanded={expanded}
          onClick={() => setExpanded((v) => !v)}
          className="inline-flex items-center justify-center gap-1.5 self-center text-sm font-medium text-brand hover:text-brand-hover"
        >
          {expanded ? "Свернуть" : `Показать все (${CHANNEL_ORDER.length})`}
          <ChevronDown size={16} className={`transition-transform ${expanded ? "rotate-180" : ""}`} aria-hidden="true" />
        </button>
      )}

      <div>
        <p className="mb-2 text-sm text-ink-muted">Загрузите дополнительные файлы о бизнесе (необязательно)</p>
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          className="flex w-full flex-col items-center gap-1.5 rounded-2xl border-2 border-dashed border-border bg-surface-soft px-6 py-8 text-center transition hover:border-brand/50"
        >
          <Upload size={24} className="text-brand" aria-hidden="true" />
          <span className="text-sm font-medium text-ink">Прайс, презентация, каталог</span>
          <span className="text-xs text-ink-muted">PDF, DOC, XLSX (макс. 10 файлов)</span>
        </button>
        <input ref={fileRef} type="file" multiple hidden onChange={(e) => addFiles(e.target.files)} />
        {input.files.length > 0 && (
          <ul className="mt-3 flex flex-col gap-1.5">
            {input.files.map((name, i) => (
              <li
                key={`${name}-${i}`}
                className="flex items-center justify-between rounded-lg bg-surface-soft px-3 py-2 text-sm text-ink"
              >
                <span className="truncate">{name}</span>
                <button
                  type="button"
                  aria-label="Удалить файл"
                  onClick={() => updateInput({ files: input.files.filter((_, j) => j !== i) })}
                  className="text-ink-muted hover:text-ink"
                >
                  <X size={16} aria-hidden="true" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
