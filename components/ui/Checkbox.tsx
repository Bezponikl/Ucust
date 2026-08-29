import type { InputHTMLAttributes } from "react";

/** Кастомный чекбокс в фирменном стиле (скруглённый, бренд-заливка + белая галочка).
 *  Пробрасывает нативные пропсы (checked/defaultChecked/onChange/required и т.д.). */
export default function Checkbox({ className = "", ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <span className={`relative inline-flex h-[1.125rem] w-[1.125rem] shrink-0 ${className}`}>
      <input
        type="checkbox"
        {...props}
        className="peer h-full w-full cursor-pointer appearance-none rounded-[6px] border border-border bg-surface-soft transition checked:border-brand checked:bg-brand"
      />
      <svg
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 m-auto hidden h-3 w-3 text-white peer-checked:block"
      >
        <path d="M5 12l5 5L20 6" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  );
}
