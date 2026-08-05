"use client";

import { useState } from "react";
import Icon from "@/components/ui/Icon";
import { INVESTOR_EMAIL } from "@/lib/investors";

const inputCls =
  "rounded-2xl border border-border bg-surface-soft px-4 py-3 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card";

const isEmail = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);

// Пока без бэкенда: собираем письмо и открываем почтовый клиент пользователя.
// Позже заменить тело функции на серверный POST — UI менять не нужно.
function submitLead(data: { name: string; email: string; message: string }) {
  const subject = encodeURIComponent("Инвестиции — UCust");
  const body = encodeURIComponent(
    `Имя: ${data.name}\nEmail: ${data.email}\n\n${data.message}`,
  );
  window.location.href = `mailto:${INVESTOR_EMAIL}?subject=${subject}&body=${body}`;
}

export default function InvestorContactForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [emailError, setEmailError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isEmail(email)) {
      setEmailError("Проверьте адрес почты");
      return;
    }
    setEmailError(null);
    submitLead({ name, email, message });
    setSent(true);
  };

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4">
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-medium text-ink">Имя</span>
        <input
          type="text"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Как к вам обращаться"
          className={inputCls}
        />
      </label>

      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-medium text-ink">Email</span>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onBlur={() => setEmailError(email && !isEmail(email) ? "Проверьте адрес почты" : null)}
          placeholder="you@example.com"
          aria-invalid={Boolean(emailError)}
          className={inputCls}
        />
        {emailError && (
          <span className="text-xs text-[color:var(--error,#e5484d)]" role="alert">
            {emailError}
          </span>
        )}
      </label>

      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-medium text-ink">Сообщение</span>
        <textarea
          required
          rows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Коротко о вашем интересе"
          className={`${inputCls} resize-y`}
        />
      </label>

      <button
        type="submit"
        className="btn-glass-blue mt-1 inline-flex w-full items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold"
      >
        Отправить <Icon name="arrow-right" size={16} aria-hidden="true" />
      </button>

      <p className="text-xs leading-relaxed text-ink-muted" aria-live="polite">
        {sent
          ? "Откроется ваш почтовый клиент с готовым письмом. Если он не открылся — напишите нам напрямую."
          : "Кнопка откроет ваш почтовый клиент с заполненным письмом."}
      </p>
    </form>
  );
}
