import type { ReactNode } from "react";
import type { LegalBlock } from "@/lib/legal.types";

/**
 * Отрисовка правового документа. Разметка в исходниках юриста ограничена
 * заголовками, списками и жирным начертанием — полноценный markdown-рендерер
 * здесь был бы лишним весом, поэтому inline-разбор ровно на **жирный**.
 */
function inline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean).map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={i} className="font-semibold text-ink">
        {part.slice(2, -2)}
      </strong>
    ) : (
      <span key={i}>{part}</span>
    ),
  );
}

export default function LegalBody({ blocks }: { blocks: LegalBlock[] }) {
  return (
    <div className="flex flex-col gap-4">
      {blocks.map((b, i) => {
        if (b.t === "h") {
          return (
            // scroll-mt — чтобы якорь из оглавления не уезжал под липкую шапку
            <h2
              key={i}
              id={`s${i}`}
              className="scroll-mt-24 pt-3 text-base font-bold text-ink first:pt-0 sm:text-lg"
            >
              {b.text}
            </h2>
          );
        }
        if (b.t === "sub") {
          return (
            <h3 key={i} className="pt-1 text-sm font-semibold text-ink">
              {b.text}
            </h3>
          );
        }
        if (b.t === "p") {
          return (
            <p key={i} className="text-[0.9375rem] leading-relaxed text-ink-muted">
              {inline(b.text)}
            </p>
          );
        }
        if (b.t === "ul") {
          return (
            <ul key={i} className="flex flex-col gap-1.5 pl-1">
              {b.items.map((item, j) => (
                <li key={j} className="flex gap-2.5 text-[0.9375rem] leading-relaxed text-ink-muted">
                  <span aria-hidden="true" className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-brand/60" />
                  <span>{inline(item)}</span>
                </li>
              ))}
            </ul>
          );
        }
        return (
          <ol key={i} className="flex flex-col gap-2">
            {b.items.map((item, j) => (
              <li key={j} className="flex gap-2.5 text-[0.9375rem] leading-relaxed text-ink-muted">
                <span
                  aria-hidden="true"
                  className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-brand-tint text-[0.6875rem] font-bold tabular-nums text-brand"
                >
                  {j + 1}
                </span>
                <span>{inline(item)}</span>
              </li>
            ))}
          </ol>
        );
      })}
    </div>
  );
}
