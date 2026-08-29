"use client";

import { useLayoutEffect, useRef, useState, type RefObject } from "react";
import Icon from "@/components/ui/Icon";
import AnchoredPopover from "@/components/ui/AnchoredPopover";

/** Наборы под тексты постов: эмоции, жесты, еда, события, символы. */
const GROUPS: { id: string; label: string; tab: string; items: string[] }[] = [
  {
    id: "smileys",
    label: "Смайлы и эмоции",
    tab: "🙂",
    items: [
      "😀", "😃", "😄", "😁", "😊", "🙂", "😉", "😍", "🥰", "😘", "😋", "😎",
      "🤩", "🥳", "🤗", "🤔", "😌", "😴", "😇", "🙃", "😅", "😂", "🥺", "😢",
      "😮", "😱", "🤯", "😤", "🥹", "😐", "🫶", "💫",
    ],
  },
  {
    id: "gestures",
    label: "Жесты и люди",
    tab: "👍",
    items: [
      "👍", "👏", "🙌", "🤝", "🙏", "✌️", "🤞", "👌", "💪", "🫰", "👋", "☝️",
      "👇", "👉", "🧑‍🍳", "👨‍🍳", "👩‍🍳", "🧑‍💻", "👨‍👩‍👧", "🧡", "❤️", "💛", "💚", "💙",
      "💜", "🤍", "🖤", "💝", "💖", "💕", "💯", "🔥",
    ],
  },
  {
    id: "food",
    label: "Еда и напитки",
    tab: "☕",
    items: [
      "☕", "🍵", "🧋", "🥤", "🧃", "🍹", "🍸", "🥂", "🍰", "🧁", "🍪", "🥐",
      "🥯", "🍩", "🍫", "🍯", "🥗", "🍕", "🍔", "🌮", "🍣", "🍜", "🥞", "🧇",
      "🍓", "🍋", "🍊", "🫐", "🥑", "🌶️", "🧀", "🍞",
    ],
  },
  {
    id: "events",
    label: "События и места",
    tab: "🎉",
    items: [
      "🎉", "🎊", "🎁", "🎂", "🎈", "🎄", "✨", "🌟", "⭐", "🏆", "🥇", "🎯",
      "📅", "⏰", "📍", "🏠", "🏡", "🏢", "🛍️", "🛒", "🚗", "🚚", "✈️", "🌸",
      "🌿", "🌞", "🌙", "☀️", "🌈", "❄️", "🍂", "🌊",
    ],
  },
  {
    id: "symbols",
    label: "Символы",
    tab: "💬",
    items: [
      "💬", "📢", "📣", "🔔", "❗", "❓", "✅", "☑️", "❌", "⚡", "💡", "📌",
      "📎", "🔗", "📷", "🎬", "🎧", "🎵", "📱", "💻", "🖥️", "💳", "💰", "🏷️",
      "📦", "🚀", "🧭", "🔎", "📊", "📈", "🕐", "➡️",
    ],
  },
];

/**
 * Вставка эмодзи в позицию курсора текстового поля.
 * Один компонент на создание и редактирование публикации — набор и поведение общие.
 */
export default function EmojiPicker({
  targetRef,
  value,
  onChange,
  align = "right",
  label = "Вставить эмодзи",
}: {
  targetRef: RefObject<HTMLTextAreaElement | null>;
  value: string;
  onChange: (next: string) => void;
  align?: "left" | "right";
  label?: string;
}) {
  const [open, setOpen] = useState(false);
  const [group, setGroup] = useState(GROUPS[0].id);
  const wrap = useRef<HTMLDivElement>(null);

  // Каретку ставим после того, как React отрисует новое значение поля
  const caret = useRef<number | null>(null);
  useLayoutEffect(() => {
    if (caret.current === null) return;
    const el = targetRef.current;
    if (el) {
      el.focus();
      el.setSelectionRange(caret.current, caret.current);
    }
    caret.current = null;
  }, [value, targetRef]);

  const insert = (emoji: string) => {
    const el = targetRef.current;
    if (!el) {
      onChange(value + emoji);
      return;
    }
    const start = el.selectionStart ?? value.length;
    const end = el.selectionEnd ?? start;
    caret.current = start + emoji.length;
    onChange(value.slice(0, start) + emoji + value.slice(end));
  };

  const current = GROUPS.find((g) => g.id === group) ?? GROUPS[0];

  return (
    <div ref={wrap} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-label={label}
        title={label}
        className={`flex h-8 w-8 items-center justify-center rounded-full transition duration-150 hover:bg-surface-soft ${
          open ? "bg-surface-soft text-brand" : "text-ink-muted hover:text-ink"
        }`}
      >
        <Icon name="emoji" size={17} aria-hidden="true" />
      </button>

      {/* Портал: панель редактора прокручивается, обычный поповер там обрезается */}
      <AnchoredPopover
        anchorRef={wrap}
        open={open}
        onClose={() => setOpen(false)}
        width={304}
        align={align}
        className="rounded-2xl border border-border bg-card p-2 shadow-lift"
      >
        <div role="dialog" aria-label={label}>
          <div className="mb-2 flex items-center gap-1 border-b border-border/70 pb-2">
            {GROUPS.map((g) => (
              <button
                key={g.id}
                type="button"
                onClick={() => setGroup(g.id)}
                aria-pressed={g.id === group}
                aria-label={g.label}
                title={g.label}
                className={`flex h-8 flex-1 items-center justify-center rounded-lg text-base leading-none transition duration-150 ${
                  g.id === group ? "bg-brand/10" : "opacity-60 hover:bg-surface-soft hover:opacity-100"
                }`}
              >
                <span aria-hidden="true">{g.tab}</span>
              </button>
            ))}
          </div>

          <div className="grid max-h-52 grid-cols-8 gap-0.5 overflow-y-auto">
            {current.items.map((e) => (
              <button
                key={e}
                type="button"
                onClick={() => insert(e)}
                aria-label={`Вставить ${e}`}
                className="flex h-9 items-center justify-center rounded-lg text-lg leading-none transition duration-150 hover:bg-surface-soft active:scale-95"
              >
                <span aria-hidden="true">{e}</span>
              </button>
            ))}
          </div>
        </div>
      </AnchoredPopover>
    </div>
  );
}
