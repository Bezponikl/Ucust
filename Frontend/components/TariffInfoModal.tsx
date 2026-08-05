"use client";

import Icon from "./ui/Icon";
import ModalShell from "./ModalShell";

const GROUPS: { title: string; items: string }[] = [
  {
    title: "Масштаб под вас",
    items: "Любое число публикаций, бизнесов и людей в команде.",
  },
  {
    title: "Контент",
    items: "Видео, генерация постов по запросу, акции, водяной знак бренда.",
  },
  {
    title: "Клиенты",
    items: "Единые входящие, ИИ-автоответы, CRM клиентов.",
  },
  {
    title: "Аналитика и поддержка",
    items: "Расширенная аналитика, приоритет, персональный менеджер.",
  },
];

export default function TariffInfoModal({
  open,
  onClose,
  onStart,
}: {
  open: boolean;
  onClose: () => void;
  onStart: () => void;
}) {
  return (
    <ModalShell open={open} onClose={onClose} labelledBy="tariff-info-title">
      <div className="flex items-center gap-2.5">
        <Icon name="sliders" size={22} className="shrink-0 text-brand-purple" />
        <h2 id="tariff-info-title" className="text-xl font-bold text-ink sm:text-2xl">
          Свой тариф
        </h2>
      </div>
      <p className="mt-1.5 text-sm text-ink-muted">
        Соберите тариф под свой бизнес — платите только за нужные возможности.
      </p>

      <ul className="mt-6 flex flex-col gap-4">
        {GROUPS.map((g) => (
          <li key={g.title} className="flex items-start gap-3">
            <Icon name="check-bold" size={20} className="mt-0.5 shrink-0 text-brand-purple" />
            <span>
              <span className="block text-sm font-semibold text-ink">{g.title}</span>
              <span className="block text-sm text-ink-muted">{g.items}</span>
            </span>
          </li>
        ))}
      </ul>

      <p className="mt-6 rounded-2xl bg-surface-soft px-4 py-3 text-sm text-ink-muted">
        Точную конфигурацию и цену вы соберёте в личном кабинете после регистрации.
      </p>

      <button
        type="button"
        onClick={onStart}
        className="btn-glass-blue mt-5 inline-flex w-full items-center justify-center px-6 py-3.5 text-sm font-semibold"
      >
        Начать
      </button>
    </ModalShell>
  );
}
