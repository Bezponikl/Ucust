"use client";

import { useState, type InputHTMLAttributes } from "react";
import Icon from "@/components/ui/Icon";

// pr-12: длинный пароль не подлезает под кнопку показа
const baseClass =
  "w-full rounded-full border border-border bg-surface-soft py-3 pl-4 pr-12 text-sm text-ink outline-none transition-colors placeholder:text-ink-muted focus:border-brand focus:bg-card";

export default function PasswordInput({
  className = "",
  ...props
}: InputHTMLAttributes<HTMLInputElement>) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="relative">
      <input type={visible ? "text" : "password"} className={`${baseClass} ${className}`} {...props} />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        aria-label={visible ? "Скрыть пароль" : "Показать пароль"}
        className="absolute right-3.5 top-1/2 -translate-y-1/2 text-ink-muted transition-colors hover:text-ink"
      >
        <span className="relative inline-flex h-[1.125rem] w-[1.125rem] items-center justify-center">
          <Icon name="eye" size={18} aria-hidden="true" />
          {!visible && (
            <span
              aria-hidden="true"
              className="absolute left-0 top-1/2 h-[1.5px] w-[1.1875rem] -translate-y-1/2 rotate-45 bg-current"
            />
          )}
        </span>
      </button>
    </div>
  );
}
