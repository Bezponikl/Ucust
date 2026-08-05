"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import Icon from "@/components/ui/Icon";
import type { IconName } from "@/lib/icons/solar";
import { useDashboard } from "./DashboardProvider";
import { menuSurfaceClass, topbarButtonClass } from "@/lib/dashboard/surface";

type NotifColor = "success" | "orange" | "brand" | "pink" | "purple";

interface Notif {
  id: string;
  color: NotifColor;
  icon: IconName;
  title: string;
  text: string;
  time: string;
  read: boolean;
  /** Куда ведёт уведомление — как пуш на телефоне открывает нужный экран. */
  href: string;
}

const ICON_BG: Record<NotifColor, string> = {
  success: "bg-success/15 text-success",
  orange:  "bg-brand-orange/15 text-brand-orange",
  brand:   "bg-brand/15 text-brand",
  pink:    "bg-brand-pink/15 text-brand-pink",
  purple:  "bg-brand-purple/15 text-brand-purple",
};

const INITIAL: Notif[] = [
  { id: "n1", color: "success", icon: "check-bold",   title: "Пост опубликован",        text: "«Летняя акция» опубликована в VK и Telegram",             time: "2 ч. назад", read: false, href: "/dashboard/content" },
  { id: "n2", color: "orange",  icon: "star",          title: "Новый отзыв",             text: "Мария К. оставила отзыв — ответьте, чтобы повысить доверие", time: "3 ч. назад", read: false, href: "/dashboard/reviews" },
  { id: "n3", color: "pink",    icon: "gift",          title: "Акция активна",           text: "«День рождения» запущена, уже 12 активаций",              time: "5 ч. назад", read: false, href: "/dashboard/promos" },
  { id: "n4", color: "brand",   icon: "sparkles-bold", title: "ИИ сгенерировал контент", text: "Готово 3 поста на следующую неделю",                      time: "7 ч. назад", read: true,  href: "/dashboard/content" },
  { id: "n5", color: "purple",  icon: "trending",      title: "Рост охвата +18%",        text: "За неделю просмотры выросли до 12.5К",                    time: "Вчера",      read: true,  href: "/dashboard/analytics" },
  { id: "n6", color: "success", icon: "calendar",      title: "Контент-план готов",      text: "ИИ составил план публикаций на ближайшие 7 дней",         time: "Вчера",      read: true,  href: "/dashboard/content" },
];

export default function NotificationsPanel() {
  const { surfaceStyle } = useDashboard();
  const router = useRouter();
  const [open, setOpen]   = useState(false);
  const [items, setItems] = useState<Notif[]>(INITIAL);
  const [tab, setTab]     = useState<"all" | "unread">("all");
  const ref = useRef<HTMLDivElement>(null);

  const unreadCount = items.filter((n) => !n.read).length;
  const visible     = tab === "all" ? items : items.filter((n) => !n.read);

  useEffect(() => {
    if (!open) return;
    const onMouse = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", onMouse);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onMouse);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const markRead = (id: string) =>
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));

  const markAll = () => setItems((prev) => prev.map((n) => ({ ...n, read: true })));

  /** Открыть уведомление: перейти в раздел и пометить прочитанным. */
  const open_ = (n: Notif) => {
    markRead(n.id);
    setOpen(false);
    router.push(n.href);
  };

  return (
    <div ref={ref} className="relative">
      {/* Кнопка-колокольчик */}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label="Уведомления"
        aria-expanded={open}
        className={`${topbarButtonClass(surfaceStyle)} relative flex h-10 w-10 items-center justify-center hover:text-ink`}
      >
        <Icon name="bell" size={18} aria-hidden="true" />
        {/* Кольцо в цвет фона: бейдж не сливается с соседним аватаром */}
        {unreadCount > 0 && (
          <span className="absolute right-0 top-0 flex h-[1.0625rem] min-w-[1.0625rem] items-center justify-center rounded-full bg-brand px-1 text-[0.625rem] font-bold text-white ring-2 ring-canvas">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {/* Выпадающая панель */}
      {open && (
        <div
          role="dialog"
          aria-label="Уведомления"
          className={`absolute right-0 top-[calc(100%+10px)] z-50 w-[340px] overflow-hidden rounded-[20px] border border-border shadow-lift sm:w-[380px] ${menuSurfaceClass(surfaceStyle)}`}
        >
          {/* Заголовок */}
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <span className="text-sm font-bold text-ink">Уведомления</span>
            <div className="flex items-center gap-3">
              {unreadCount > 0 && (
                <button type="button" onClick={markAll}
                  className="text-xs font-medium text-brand transition hover:opacity-70">
                  Отметить все
                </button>
              )}
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label="Закрыть"
                className="flex h-6 w-6 items-center justify-center rounded-full text-ink-muted transition hover:bg-surface-soft hover:text-ink"
              >
                <Icon name="close" size={14} aria-hidden="true" />
              </button>
            </div>
          </div>

          {/* Табы */}
          <div className="flex border-b border-border px-4">
            {(["all", "unread"] as const).map((t) => (
              <button key={t} type="button" onClick={() => setTab(t)}
                className={`mr-4 border-b-2 py-2.5 text-xs font-semibold transition ${
                  tab === t
                    ? "border-brand text-brand"
                    : "border-transparent text-ink-muted hover:text-ink"
                }`}>
                {t === "all"
                  ? "Все"
                  : `Непрочитанные${unreadCount > 0 ? ` (${unreadCount})` : ""}`}
              </button>
            ))}
          </div>

          {/* Список */}
          <ul className="max-h-[380px] overflow-y-auto">
            {visible.length === 0 ? (
              <li className="flex flex-col items-center gap-2 py-10 text-center">
                <span className="text-2xl" aria-hidden="true">✅</span>
                <p className="text-sm font-semibold text-ink">Всё прочитано</p>
                <p className="text-xs text-ink-muted">Новых уведомлений нет</p>
              </li>
            ) : (
              visible.map((n) => (
                <li key={n.id}>
                  {/* Клик открывает нужный раздел и заодно помечает прочитанным */}
                  <button
                    type="button"
                    onClick={() => open_(n)}
                    className={`flex w-full items-start gap-3 px-4 py-3.5 text-left transition hover:bg-surface-soft ${
                      !n.read ? "bg-brand/5" : ""
                    }`}
                  >
                    <span className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${ICON_BG[n.color]}`}>
                      <Icon name={n.icon} size={14} aria-hidden="true" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="flex items-start justify-between gap-2">
                        <span className={`text-sm leading-tight ${!n.read ? "font-semibold text-ink" : "font-medium text-ink"}`}>
                          {n.title}
                        </span>
                        <span className="shrink-0 text-[0.625rem] text-ink-muted">{n.time}</span>
                      </span>
                      <span className="mt-0.5 block text-xs leading-snug text-ink-muted">{n.text}</span>
                    </span>
                    {!n.read && (
                      <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-brand" aria-hidden="true" />
                    )}
                  </button>
                </li>
              ))
            )}
          </ul>

          {/* Футер */}
          {visible.length > 0 && (
            <div className="border-t border-border px-4 py-3">
              <button type="button"
                className="w-full text-center text-xs font-medium text-brand transition hover:opacity-70">
                Смотреть все уведомления
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
