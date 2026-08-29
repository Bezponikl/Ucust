"use client";

import { useRef } from "react";
import Icon from "@/components/ui/Icon";
import { useOnboarding } from "@/components/onboarding/OnboardingProvider";

const MAX_FILES = 10;

/**
 * Материалы о бизнесе — прайс, презентация, каталог. Живёт на шаге «О бизнесе»
 * вместо текстового описания: документы рассказывают о бизнесе точнее.
 */
export default function FileUpload() {
  const { input, updateInput } = useOnboarding();
  const fileRef = useRef<HTMLInputElement>(null);

  const addFiles = (list: FileList | null) => {
    if (!list) return;
    const names = Array.from(list).map((f) => f.name);
    updateInput({ files: [...input.files, ...names].slice(0, MAX_FILES) });
  };

  return (
    <div>
      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-ink-muted">
        Материалы о бизнесе (необязательно)
      </span>
      <button
        type="button"
        onClick={() => fileRef.current?.click()}
        className="flex w-full flex-col items-center gap-1.5 rounded-2xl border-2 border-dashed border-border bg-surface-soft px-6 py-8 text-center transition hover:border-brand/50"
      >
        <Icon name="upload" size={24} className="text-brand" aria-hidden="true" />
        <span className="text-sm font-medium text-ink">Прайс, презентация, каталог</span>
        <span className="text-xs text-ink-muted">PDF, DOC, XLSX (макс. {MAX_FILES} файлов)</span>
      </button>
      <input ref={fileRef} type="file" multiple hidden onChange={(e) => addFiles(e.target.files)} />
      {input.files.length > 0 && (
        <ul className="mt-3 flex flex-col gap-1.5">
          {input.files.map((name, i) => (
            <li
              key={`${name}-${i}`}
              className="flex items-center justify-between rounded-lg bg-surface-soft px-3 py-2 text-sm text-ink"
            >
              <span className="truncate">{name}</span>
              <button
                type="button"
                aria-label="Удалить файл"
                onClick={() => updateInput({ files: input.files.filter((_, j) => j !== i) })}
                className="text-ink-muted hover:text-ink"
              >
                <Icon name="close" size={16} aria-hidden="true" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
