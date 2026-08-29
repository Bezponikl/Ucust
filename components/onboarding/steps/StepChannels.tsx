"use client";

import { useState } from "react";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
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
  const [expanded, setExpanded] = useState(false);

  const toggle = (id: ChannelId) => {
    const connected = input.socials.includes(id);
    updateInput({ socials: connected ? input.socials.filter((s) => s !== id) : [...input.socials, id] });
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
              {connected && <Icon name="check" size={18} className="ml-auto text-brand" aria-hidden="true" />}
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
          <Icon name="chevron-down" size={16} className={`transition-transform ${expanded ? "rotate-180" : ""}`} aria-hidden="true" />
        </button>
      )}

    </div>
  );
}
