"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import ModalShell from "@/components/ModalShell";
import Icon from "@/components/ui/Icon";
import type { ChannelMeta } from "@/lib/channels";
import { verifySocial } from "@/lib/api/orchestration";
import { toMessage } from "@/lib/api/errors";

/**
 * Окно привязки канала к проекту. Для Telegram верификация best-effort: бэк из
 * некоторых сетей не достаёт api.telegram.org, поэтому при неудаче канал можно
 * подключить вручную — гарантию публикации дадут уже боевые коннекторы.
 */
export default function ChannelConnectModal({
  open,
  onClose,
  channel,
  connected,
  handle,
  onSave,
  onDisconnect,
}: {
  open: boolean;
  onClose: () => void;
  channel: ChannelMeta;
  /** Канал уже привязан к проекту. */
  connected: boolean;
  /** Текущий привязанный @хэндл/ссылка (пусто, если канал не подключён). */
  handle: string;
  /** Сохранить привязку — родитель пишет канал в проект и обновляет состояние. */
  onSave: (reference: string) => Promise<void>;
  /** Отвязать канал. */
  onDisconnect: () => Promise<void>;
}) {
  const [draft, setDraft] = useState("");
  const [verified, setVerified] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // При каждом открытии показываем актуальную привязку и сбрасываем проверку.
  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect */
    setDraft(handle ?? "");
    setVerified(null);
    setError(null);
    setBusy(false);
    /* eslint-enable react-hooks/set-state-in-effect */
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, [open]);

  const verify = async () => {
    const reference = draft.trim();
    if (!reference) {
      setError("Введите @хэндл или ссылку на канал");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const result = await verifySocial(channel.id, reference);
      setVerified(result.verified);
      if (!result.verified) {
        setError("Не удалось подтвердить канал — проверьте ссылку или подключите вручную");
      }
    } catch (e) {
      setError(toMessage(e));
    } finally {
      setBusy(false);
    }
  };

  const save = async () => {
    const reference = draft.trim();
    if (!reference) {
      setError("Введите @хэндл или ссылку на канал");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await onSave(reference);
      onClose();
    } catch (e) {
      setError(toMessage(e));
      setBusy(false);
    }
  };

  const disconnect = async () => {
    setBusy(true);
    setError(null);
    try {
      await onDisconnect();
      onClose();
    } catch (e) {
      setError(toMessage(e));
      setBusy(false);
    }
  };

  const canSubmit = draft.trim().length > 0 && !busy;
  const primaryLabel = busy
    ? "Работаем…"
    : connected
      ? "Сохранить"
      : verified === true
        ? "Подключить"
        : "Проверить";

  return (
    <ModalShell open={open} onClose={onClose} labelledBy="channel-connect-title">
      <div className="flex flex-col gap-5">
        <div className="flex items-start gap-3">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-surface-soft">
            <Image
              src={channel.icon ?? ""}
              alt=""
              width={28}
              height={28}
              className="h-7 w-7 object-contain"
              aria-hidden="true"
            />
          </span>
          <div>
            <h2 id="channel-connect-title" className="text-lg font-bold text-ink">
              {channel.label}
            </h2>
            <p className="mt-0.5 text-sm text-ink-muted">
              Привязанный канал даёт ИИ контекст бренда и открывает анализ канала.
            </p>
          </div>
        </div>

        {connected && (
          <p className="flex items-center gap-2 rounded-xl bg-surface-soft px-3.5 py-2.5 text-sm text-ink">
            <Icon name="check" size={16} className="text-brand" aria-hidden="true" />
            Подключено{handle ? <> · {handle}</> : null}
          </p>
        )}

        <div>
          <span className="mb-1.5 block text-sm font-semibold text-ink">Ссылка на канал</span>
          <input
            value={draft}
            onChange={(e) => {
              setDraft(e.target.value);
              setVerified(null);
              setError(null);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && canSubmit) {
                if (connected || verified === true) void save();
                else void verify();
              }
            }}
            placeholder="@username или t.me/username"
            disabled={busy}
            autoFocus
            aria-label="Ссылка или @хэндл канала"
            className="w-full rounded-xl border border-border bg-surface-soft px-3 py-2 text-sm text-ink outline-none transition focus:border-brand"
          />
          <p className="mt-1.5 text-xs leading-relaxed text-ink-muted">
            Бэкенд проверит, что канал существует. Привязанный канал используется для анализа и как
            контекст генерации.
          </p>
        </div>

        {verified === true && (
          <p className="flex items-center gap-1.5 text-sm text-success">
            <Icon name="check" size={16} aria-hidden="true" /> Канал найден — можно подключить
          </p>
        )}
        {error && (
          <p className="flex items-center gap-1.5 text-sm text-red-500">
            <Icon name="help" size={16} aria-hidden="true" /> {error}
          </p>
        )}

        {verified === false && !connected && (
          <button
            type="button"
            onClick={() => void save()}
            disabled={busy}
            className="self-start text-sm font-medium text-brand hover:text-brand-hover disabled:opacity-60"
          >
            Всё равно подключить
          </button>
        )}

        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <button
            type="button"
            onClick={() => {
              if (connected || verified === true) void save();
              else void verify();
            }}
            disabled={!canSubmit}
            className="inline-flex items-center justify-center gap-2 rounded-full bg-brand px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-hover disabled:opacity-60"
          >
            <Icon name="link" size={16} aria-hidden="true" /> {primaryLabel}
          </button>
          {connected && (
            <button
              type="button"
              onClick={() => void disconnect()}
              disabled={busy}
              className="inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold text-red-500 transition hover:bg-red-500/10 disabled:opacity-60"
            >
              <Icon name="trash" size={16} aria-hidden="true" /> Отключить
            </button>
          )}
        </div>
      </div>
    </ModalShell>
  );
}