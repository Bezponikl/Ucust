"use client";

import { useEffect, useRef, useState, type ChangeEvent } from "react";
import Image from "next/image";
import Icon from "@/components/ui/Icon";
import { CHANNELS } from "@/lib/channels";
import type { ChatMessage, InboxItem } from "@/lib/dashboard/inbox";
import { useDashboard } from "@/components/dashboard/DashboardProvider";
import { menuSurfaceClass } from "@/lib/dashboard/surface";

const EMOJIS = ["😊", "👍", "❤️", "🎉", "☕", "🙌", "🔥", "😍", "🙏", "✨", "😂", "👌", "😅", "🥰", "👋", "💚", "😉", "🤝"];

/** Чат сообщения: занимает всю высоту родительской правой панели.
 *  Скролит только лента сообщений; шапка и композер фиксированы. */
export default function ChatPanel({ item, onBack }: { item: InboxItem; onBack: () => void }) {
  const { surfaceStyle } = useDashboard();
  const ch = item.channel ? CHANNELS[item.channel] : null;

  const initial: ChatMessage[] =
    item.thread ??
    [
      { from: "them", text: item.text, time: item.time },
      ...(item.answered && item.sentReply ? [{ from: "me" as const, text: item.sentReply, time: item.time }] : []),
    ];

  const [msgs, setMsgs]         = useState<ChatMessage[]>(initial);
  const [text, setText]         = useState("");
  const [emojiOpen, setEmojiOpen] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const taRef     = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [msgs]);

  const autosize = () => {
    const el = taRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 132)}px`;
  };
  const setInput = (v: string) => { setText(v); requestAnimationFrame(autosize); };

  const send = () => {
    const t = text.trim();
    if (!t) return;
    setMsgs((m) => [...m, { from: "me", text: t, time: "сейчас" }]);
    setText("");
    if (taRef.current) taRef.current.style.height = "auto";
  };
  const onFile = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) setMsgs((m) => [...m, { from: "me", text: `📎 ${f.name}`, time: "сейчас" }]);
    e.target.value = "";
  };

  return (
    <div className="flex h-full flex-col">
      {/* Шапка */}
      <div className="flex h-[72px] shrink-0 items-center gap-3 border-b border-border/40 px-6">
        <button
          type="button"
          onClick={onBack}
          aria-label="Назад"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-ink-muted transition hover:bg-surface-soft lg:hidden"
        >
          <Icon name="arrow-left" size={18} aria-hidden="true" />
        </button>
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-brand/12 text-sm font-semibold text-brand">
          {item.author.slice(0, 1)}
        </span>
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold text-ink">{item.author}</div>
          <div className="flex items-center gap-1 text-xs text-ink-muted">
            {ch?.icon && ch.iconType !== "wordmark" ? (
              <Image src={ch.icon} alt="" width={13} height={13} className="h-[0.8125rem] w-[0.8125rem] object-contain" aria-hidden="true" />
            ) : null}
            {item.sourceLabel} · онлайн
          </div>
        </div>
      </div>

      {/* Лента сообщений — только этот блок скролит */}
      <div
        ref={scrollRef}
        className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto bg-surface-soft/20 px-4 py-4"
      >
        {msgs.map((m, i) => (
          <div key={i} className={`flex ${m.from === "me" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[78%] min-w-0 rounded-2xl px-3.5 py-2 text-sm leading-relaxed ${
                m.from === "me"
                  ? "rounded-br-md bg-brand text-white"
                  : "rounded-bl-md bg-card text-ink shadow-soft"
              }`}
            >
              <p className="whitespace-pre-wrap break-words">{m.text}</p>
              <div className={`mt-0.5 text-right text-[0.625rem] ${m.from === "me" ? "text-white/70" : "text-ink-muted"}`}>
                {m.time}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Композер */}
      <div className="shrink-0 border-t border-border/40 px-3 py-2.5">
        <div className="flex items-end gap-0.5 rounded-3xl border border-border bg-surface-soft px-1.5 py-1">
          <button
            type="button"
            onClick={() => fileInput.current?.click()}
            aria-label="Прикрепить файл"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-ink-muted transition hover:bg-card hover:text-ink"
          >
            <Icon name="image-plus" size={18} aria-hidden="true" />
          </button>
          <textarea
            ref={taRef}
            rows={1}
            value={text}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Сообщение…"
            className="max-h-[132px] min-w-0 flex-1 resize-none border-0 bg-transparent px-1.5 py-2 text-sm leading-relaxed text-ink outline-none placeholder:text-ink-muted"
          />

          {/* Эмодзи */}
          <div className="relative shrink-0">
            <button
              type="button"
              onClick={() => setEmojiOpen((v) => !v)}
              aria-label="Эмодзи"
              aria-expanded={emojiOpen}
              className="flex h-9 w-9 items-center justify-center rounded-full text-ink-muted transition hover:bg-card hover:text-ink"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
                strokeLinecap="round" strokeLinejoin="round" className="h-[1.1875rem] w-[1.1875rem]" aria-hidden="true">
                <circle cx="12" cy="12" r="9" />
                <path d="M8.5 14.5c.9 1 2.1 1.5 3.5 1.5s2.6-.5 3.5-1.5" />
                <circle cx="9" cy="9.8" r="0.5" fill="currentColor" stroke="none" />
                <circle cx="15" cy="9.8" r="0.5" fill="currentColor" stroke="none" />
              </svg>
            </button>
            {emojiOpen && (
              <>
                <button type="button" aria-hidden className="fixed inset-0 z-10 cursor-default" onClick={() => setEmojiOpen(false)} />
                <div className={`absolute bottom-full right-0 z-20 mb-2 grid w-60 grid-cols-6 gap-1 rounded-2xl border border-border p-2 shadow-lift ${menuSurfaceClass(surfaceStyle)}`}>
                  {EMOJIS.map((e) => (
                    <button
                      key={e}
                      type="button"
                      onClick={() => setInput(text + e)}
                      className="flex h-8 w-8 items-center justify-center rounded-lg text-lg transition hover:bg-surface-soft"
                    >
                      {e}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          {text.trim() ? (
            <button
              type="button"
              onClick={send}
              aria-label="Отправить"
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand text-white transition hover:brightness-110"
            >
              <Icon name="send" size={16} aria-hidden="true" />
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setInput(item.aiDraft)}
              aria-label="Сгенерировать ответ ИИ"
              title="ИИ-ответ"
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-brand transition hover:bg-brand/10"
            >
              <Icon name="sparkles" size={18} aria-hidden="true" />
            </button>
          )}
        </div>
        <input ref={fileInput} type="file" hidden onChange={onFile} />
      </div>
    </div>
  );
}
