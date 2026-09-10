"use client";

import { useState } from "react";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";
import { CHANNELS, CHANNEL_ORDER, CONNECTIBLE_CHANNELS, type ChannelId, type ChannelMeta } from "@/lib/channels";
import { verifySocial } from "@/lib/api/orchestration";
import { toMessage } from "@/lib/api/errors";

const DEFAULT_VISIBLE = 4;

function ChannelBadge({ channel, dimmed = false }: { channel: ChannelMeta; dimmed?: boolean }) {
  const dim = dimmed ? " opacity-50 saturate-0" : "";
  if (channel.icon && channel.iconType !== "wordmark") {
    return (
      <span className={`flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-surface-soft${dim}`}>
        <Image src={channel.icon} alt="" width={28} height={28} className="h-7 w-7 object-contain" aria-hidden="true" />
      </span>
    );
  }
  return (
    <span
      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-xs font-bold text-white${dim}`}
      style={{ backgroundColor: channel.colorVar }}
      aria-hidden="true"
    >
      {channel.short}
    </span>
  );
}

/**
 * Подключение канала. Для telegram проверка временно пропущена: бэк из RU-сети
 * не достаёт t.me/api.telegram.org, поэтому verified всегда false и без пропуска
 * канал было бы невозможно привязать. Остальные каналы — по-прежнему через
 * verifySocial (только при verified=true соцсеть попадает в input.socials).
 */
function VerifyFlow({ channel, onDone }: { channel: ChannelMeta; onDone: () => void }) {
  const { input, updateInput } = useOnboarding();
  const [draft, setDraft] = useState(input.channelHandles?.[channel.id] ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const skipVerify = channel.id === "telegram";

  const connect = async () => {
    const reference = draft.trim();
    if (!reference) {
      setError("Введите @хэндл или ссылку на канал");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      if (!skipVerify) {
        const result = await verifySocial(channel.id, reference);
        if (!result.verified) {
          setError(result.error === "UNSUPPORTED_CHANNEL" ? "Канал пока не поддерживается" : "Не удалось найти канал — проверьте ссылку");
          return;
        }
      }
      const handles = { ...input.channelHandles, [channel.id]: reference };
      const socials = input.socials.includes(channel.id) ? input.socials : [...input.socials, channel.id];
      updateInput({ socials, channelHandles: handles });
      onDone();
    } catch (e) {
      setError(toMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex w-full items-center gap-2">
      <input
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && !busy && connect()}
        placeholder="@username или t.me/username"
        autoFocus
        disabled={busy}
        aria-label={`Ссылка или @хэндл для ${channel.label}`}
        className="w-full min-w-0 rounded-xl border border-border bg-surface-soft px-3 py-2 text-sm text-ink outline-none focus:border-brand"
      />
      <button
        type="button"
        onClick={connect}
        disabled={busy}
        className="shrink-0 rounded-xl bg-brand px-3 py-2 text-sm font-semibold text-white transition hover:bg-brand-hover disabled:opacity-60"
      >
        {busy ? (skipVerify ? "Подключаем…" : "Проверяем…") : skipVerify ? "Подключить" : "Проверить"}
      </button>
      {error && <span className="text-xs text-red-500">{error}</span>}
    </div>
  );
}

export default function StepChannels() {
  const { input, updateInput } = useOnboarding();
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState<ChannelId | null>(null);

  const disconnect = (id: ChannelId) => {
    const handles = { ...(input.channelHandles ?? {}) };
    delete handles[id];
    updateInput({ socials: input.socials.filter((s) => s !== id), channelHandles: handles });
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
          const available = CONNECTIBLE_CHANNELS.includes(id);
          const connected = available && input.socials.includes(id);
          const isEditing = editing === id;

          const card = (
            <button
              type="button"
              aria-pressed={connected}
              disabled={!available}
              onClick={() => {
                if (connected) {
                  disconnect(id);
                  setEditing((v) => (v === id ? null : v));
                } else if (available) {
                  setEditing((v) => (v === id ? null : id));
                }
              }}
              className={`flex w-full items-center gap-3 rounded-2xl border bg-card px-4 py-3.5 text-left transition ${
                connected
                  ? "border-brand ring-1 ring-brand"
                  : isEditing
                    ? "border-brand/50 ring-1 ring-brand/30"
                    : available
                      ? "border-border hover:border-brand/50"
                      : "cursor-not-allowed border-border opacity-60"
              }`}
            >
              <ChannelBadge channel={channel} dimmed={!available} />
              <span className="leading-tight">
                <span className={`block text-sm font-semibold ${available ? "text-ink" : "text-ink-muted"}`}>
                  {channel.label}
                </span>
                <span className={`block text-xs ${connected ? "text-brand" : "text-ink-muted"}`}>
                  {connected
                    ? `Подключено · ${input.channelHandles?.[id] ?? ""}`
                    : isEditing
                      ? "Введите ссылку на канал"
                      : available
                        ? "Нажмите для подключения"
                        : "Пока не доступно"}
                </span>
              </span>
              {connected && <Icon name="check" size={18} className="ml-auto text-brand" aria-hidden="true" />}
            </button>
          );

          return (
            <div key={id} className="flex flex-col gap-2">
              {isEditing && available ? (
                <VerifyFlow
                  channel={channel}
                  onDone={() => setEditing(null)}
                />
              ) : null}
              {available ? card : <div title="Пока не доступно" className="cursor-not-allowed">{card}</div>}
            </div>
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
          <Icon name="chevron-down" size={16} className={`transition-transform ${expanded ? "rotate-180" : ""}`} aria-hidden="true" />
        </button>
      )}
    </div>
  );
}