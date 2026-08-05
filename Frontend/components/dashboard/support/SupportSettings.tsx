"use client";

import { useState } from "react";
import Icon from "@/components/ui/Icon";
import { SettingsCard, SelectField, TextArea } from "@/components/dashboard/settings/primitives";
import { SUPPORT_FAQ, SUPPORT_TICKETS, SUPPORT_CONTACTS, type SupportTicket } from "@/lib/dashboard/support";
import { toast } from "@/lib/toast";

const SUBJECTS = ["Технический вопрос", "Вопрос по оплате", "Другое"];

function FaqRow({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border-b border-border/40 py-3 last:border-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-2 text-left text-sm font-medium text-ink"
      >
        {q}
        <Icon
          name="chevron-down"
          size={15}
          className={`shrink-0 text-ink-muted transition-transform ${open ? "rotate-180" : ""}`}
          aria-hidden="true"
        />
      </button>
      {open && <p className="mt-2 text-sm text-ink-muted">{a}</p>}
    </div>
  );
}

export default function SupportSettings() {
  const [subject, setSubject] = useState(SUBJECTS[0]);
  const [message, setMessage] = useState("");
  const [tickets, setTickets] = useState<SupportTicket[]>(SUPPORT_TICKETS);

  const submit = () => {
    if (!message.trim()) return;
    const next: SupportTicket = {
      id: `t-${tickets.length + 1}-${subject}`,
      subject,
      message,
      date: "только что",
      status: "Открыт",
    };
    setTickets((t) => [next, ...t]);
    setMessage("");
    toast("Обращение отправлено");
  };

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-xl font-bold text-ink sm:text-2xl">Поддержка</h1>
        <p className="mt-0.5 text-sm text-ink-muted">Контакты, обращения и частые вопросы</p>
      </div>

      <SettingsCard title="Контакты">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <a
            href={`mailto:${SUPPORT_CONTACTS.email}`}
            className="flex items-center gap-3 rounded-2xl border border-border bg-surface-soft px-4 py-3 shadow-soft transition hover:-translate-y-0.5 hover:border-brand/30 hover:shadow-lift"
          >
            <Icon name="mail" size={18} className="shrink-0 text-ink-muted" aria-hidden="true" />
            <span className="truncate text-sm text-ink">{SUPPORT_CONTACTS.email}</span>
          </a>
          <a
            href={`https://t.me/${SUPPORT_CONTACTS.telegram.replace("@", "")}`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-3 rounded-2xl border border-border bg-surface-soft px-4 py-3 shadow-soft transition hover:-translate-y-0.5 hover:border-brand/30 hover:shadow-lift"
          >
            <Icon name="send" size={18} className="shrink-0 text-ink-muted" aria-hidden="true" />
            <span className="truncate text-sm text-ink">{SUPPORT_CONTACTS.telegram}</span>
          </a>
          <a
            href={`tel:${SUPPORT_CONTACTS.phone.replace(/\s/g, "")}`}
            className="flex items-center gap-3 rounded-2xl border border-border bg-surface-soft px-4 py-3 shadow-soft transition hover:-translate-y-0.5 hover:border-brand/30 hover:shadow-lift"
          >
            <Icon name="phone" size={18} className="shrink-0 text-ink-muted" aria-hidden="true" />
            <span className="truncate text-sm text-ink">{SUPPORT_CONTACTS.phone}</span>
          </a>
        </div>
      </SettingsCard>

      <SettingsCard title="Написать в поддержку">
        <div className="flex flex-col gap-4">
          <SelectField label="Тема" value={subject} onChange={setSubject} options={SUBJECTS} />
          <TextArea label="Сообщение" value={message} onChange={setMessage} placeholder="Опишите проблему или вопрос" />
          <button
            type="button"
            onClick={submit}
            className="btn-glass-blue inline-flex w-fit items-center justify-center px-5 py-2.5 text-sm font-semibold"
          >
            Отправить обращение
          </button>
        </div>
      </SettingsCard>

      <SettingsCard title="Частые вопросы">
        {SUPPORT_FAQ.map((item) => (
          <FaqRow key={item.q} q={item.q} a={item.a} />
        ))}
      </SettingsCard>

      <SettingsCard title="История обращений">
        <ul className="flex flex-col gap-2">
          {tickets.map((t) => (
            <li key={t.id} className="flex items-center gap-3 rounded-2xl border border-border bg-surface-soft px-4 py-3">
              <Icon name="message" size={18} className="shrink-0 text-ink-muted" aria-hidden="true" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-ink">{t.subject}</p>
                <p className="truncate text-xs text-ink-muted">{t.date}</p>
              </div>
              <span className={`shrink-0 text-xs font-medium ${t.status === "Открыт" ? "text-brand" : "text-ink-muted"}`}>
                {t.status}
              </span>
            </li>
          ))}
        </ul>
      </SettingsCard>
    </div>
  );
}
